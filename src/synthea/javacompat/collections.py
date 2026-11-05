"""Java 21 collection order, including linked collision bins and red-black tree bins.

Java: java.util.HashMap/HashSet/LinkedHashMap/TreeMap and java.util.concurrent.ConcurrentHashMap.
The concurrent variant models deterministic single-threaded operations, not JVM synchronization.
"""

from __future__ import annotations

import math
import struct
from collections.abc import (
    Callable,
    ItemsView,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSet,
    ValuesView,
)
from dataclasses import dataclass, field
from typing import Protocol, cast, runtime_checkable

from synthea.javacompat.hashing import (
    KeyType,
    character_hash_code,
    double_to_long_bits,
    java_hash_code,
    string_compare_to,
    utf16_units,
)

_MAXIMUM_CAPACITY = 1 << 30


@runtime_checkable
class JavaComparable(Protocol):
    """Java: Comparable#compareTo; caller-supplied custom comparable key boundary."""

    def java_compare_to(self, other: object) -> int:
        """Java: Comparable#compareTo."""
        ...


@runtime_checkable
class JavaIdentityHashable(Protocol):
    """Java: System#identityHashCode; explicit Java-side identity, never Python id()."""

    def java_identity_hash_code(self) -> int:
        """Java: System#identityHashCode."""
        ...


class NondeterministicJavaOrderError(ValueError):
    """Java: HashMap.TreeNode#tieBreakOrder requires a JVM-specific identity hash."""


def _float32(value: float) -> float:
    """Java: load-factor float arithmetic in HashMap#resize."""
    try:
        return struct.unpack(">f", struct.pack(">f", value))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


def _table_size_for(capacity: int) -> int:
    """Java: HashMap#tableSizeFor / ConcurrentHashMap#tableSizeFor."""
    return min(_MAXIMUM_CAPACITY, 1 << max(0, (capacity - 1).bit_length()))


def _java_equal(left: object, right: object) -> bool:
    """Java: Object#equals for supported boxed values, including NaN and signed zero."""
    if left is right:
        return True
    if left is None or right is None:
        return False
    if isinstance(left, str) and isinstance(right, str):
        return utf16_units(left) == utf16_units(right)
    if isinstance(left, bool | int | float) or isinstance(right, bool | int | float):
        if type(left) is not type(right):
            return False
        if isinstance(left, float) and isinstance(right, float):
            return double_to_long_bits(left) == double_to_long_bits(right)
    return bool(left == right)


def _class_name(value: object, key_type: KeyType | None) -> str:
    """Java: Class#getName for deterministic cross-class tree-bin tie breaking."""
    if key_type == "character":
        return "java.lang.Character"
    if isinstance(value, str):
        return "java.lang.String"
    if isinstance(value, bool):
        return "java.lang.Boolean"
    if isinstance(value, int):
        return "java.lang.Long" if key_type == "long" else "java.lang.Integer"
    if isinstance(value, float):
        return "java.lang.Double"
    name = getattr(value, "java_class_name", None)
    if name is not None:
        return str(name)
    raise NondeterministicJavaOrderError(
        "Java tree-bin cross-class tie breaking requires java_class_name metadata; "
        "a Python class name does not identify the original Java class."
    )


def _key_compare(left: object, right: object, key_type: KeyType | None) -> int:
    """Java: comparableClassFor/compareComparables followed by TreeNode#tieBreakOrder."""
    if left is None or right is None:
        return -1 if left is None else 1
    if key_type == "character":
        return character_hash_code(cast(str | int, left)) - character_hash_code(
            cast(str | int, right)
        )  # identityHashCode(null) is zero
    if type(left) is type(right):
        if isinstance(left, str) and isinstance(right, str):
            return string_compare_to(left, right)
        if isinstance(left, float) and isinstance(right, float):
            if left < right:
                return -1
            if left > right:
                return 1
            a, b = double_to_long_bits(left), double_to_long_bits(right)
            a = a - (1 << 64) if a >= 1 << 63 else a
            b = b - (1 << 64) if b >= 1 << 63 else b
            return (a > b) - (a < b)
        if isinstance(left, int) and isinstance(right, int):
            return (left > right) - (left < right)
        if isinstance(left, JavaComparable):
            result = left.java_compare_to(right)
            if result:
                return result
    else:
        difference = string_compare_to(_class_name(left, key_type), _class_name(right, key_type))
        if difference:
            return difference
    if isinstance(left, JavaIdentityHashable) and isinstance(right, JavaIdentityHashable):
        return -1 if left.java_identity_hash_code() <= right.java_identity_hash_code() else 1
    raise NondeterministicJavaOrderError(
        "Java tree-bin tieBreakOrder requires System.identityHashCode for unequal, "
        "equal-hash non-Comparable keys. Supply java_compare_to() or Java-side "
        "java_identity_hash_code(); Python identity order is not Java parity."
    )


@dataclass(eq=False, slots=True)
class _Node[K, V]:
    """Java: HashMap.Node/TreeNode; traversal order is stored separately in its bin."""

    hash: int
    key: K
    value: V
    parent: _Node[K, V] | None = None
    left: _Node[K, V] | None = None
    right: _Node[K, V] | None = None
    red: bool = False


@dataclass(slots=True)
class _Bin[K, V]:
    """Java: linked bin or TreeBin; nodes preserve the observable next-chain order."""

    nodes: list[_Node[K, V]] = field(default_factory=list)
    root: _Node[K, V] | None = None


def _rotate[K, V](root: _Node[K, V], node: _Node[K, V], left: bool) -> _Node[K, V]:
    """Java: HashMap.TreeNode#rotateLeft/rotateRight (symmetric rotations)."""
    child = node.right if left else node.left
    if child is None:
        return root
    inner = child.left if left else child.right
    if left:
        node.right = inner
    else:
        node.left = inner
    if inner is not None:
        inner.parent = node
    parent = node.parent
    child.parent = parent
    if parent is None:
        root = child
        root.red = False
    elif parent.left is node:
        parent.left = child
    else:
        parent.right = child
    if left:
        child.left = node
    else:
        child.right = node
    node.parent = child
    return root


def _balance_insertion[K, V](root: _Node[K, V], node: _Node[K, V]) -> _Node[K, V]:
    """Java: HashMap.TreeNode#balanceInsertion / ConcurrentHashMap.TreeBin#balanceInsertion."""
    node.red = True
    while True:
        parent = node.parent
        if parent is None:
            node.red = False
            return node
        grand = parent.parent
        if not parent.red or grand is None:
            return root
        parent_left = parent is grand.left
        uncle = grand.right if parent_left else grand.left
        if uncle is not None and uncle.red:
            uncle.red = parent.red = False
            grand.red = True
            node = grand
        else:
            if node is (parent.right if parent_left else parent.left):
                node = parent
                root = _rotate(root, node, parent_left)
                parent = node.parent
                grand = None if parent is None else parent.parent
            if parent is not None:
                parent.red = False
                if grand is not None:
                    grand.red = True
                    root = _rotate(root, grand, not parent_left)


def _balance_deletion[K, V](root: _Node[K, V], node: _Node[K, V]) -> _Node[K, V]:
    """Java: HashMap.TreeNode#balanceDeletion / ConcurrentHashMap.TreeBin#balanceDeletion."""
    while True:
        if node is root:
            return root
        parent = node.parent
        if parent is None:
            node.red = False
            return node
        if node.red:
            node.red = False
            return root
        node_left = parent.left is node
        sibling = parent.right if node_left else parent.left
        if sibling is not None and sibling.red:
            sibling.red = False
            parent.red = True
            root = _rotate(root, parent, node_left)
            parent = node.parent
            sibling = None if parent is None else (parent.right if node_left else parent.left)
        if sibling is None:
            assert parent is not None
            node = parent
            continue
        near = sibling.left if node_left else sibling.right
        far = sibling.right if node_left else sibling.left
        if (near is None or not near.red) and (far is None or not far.red):
            sibling.red = True
            assert parent is not None
            node = parent
        else:
            if far is None or not far.red:
                if near is not None:
                    near.red = False
                sibling.red = True
                root = _rotate(root, sibling, not node_left)
                parent = node.parent
                sibling = None if parent is None else (parent.right if node_left else parent.left)
            if sibling is not None:
                sibling.red = False if parent is None else parent.red
                far = sibling.right if node_left else sibling.left
                if far is not None:
                    far.red = False
            if parent is not None:
                parent.red = False
                root = _rotate(root, parent, node_left)
            node = root


class JavaHashMap[K, V](MutableMapping[K, V]):
    """Java: java.util.HashMap, with exact stable-JVM next-chain iteration semantics.

    Pass initial_capacity for HashMap(int), or entries for HashMap(Map). An integer
    key_type of 'long' is required for boxed Long keys; default Python int means Integer.
    """

    _concurrent = False

    def __init__(
        self,
        entries: Mapping[K, V] | Iterable[tuple[K, V]] | None = None,
        *,
        initial_capacity: int | None = None,
        load_factor: float = 0.75,
        key_type: KeyType | None = None,
    ) -> None:
        """Java: HashMap constructors; lazy allocation and float32 load-factor threshold."""
        load_factor = _float32(load_factor)
        if not load_factor > 0 or (initial_capacity is not None and initial_capacity < 0):
            raise ValueError("Invalid Java map capacity or load factor")
        self.key_type = key_type
        self._load_factor = load_factor
        self._capacity = 0
        self._threshold = 0 if initial_capacity is None else _table_size_for(initial_capacity)
        self._table: dict[int, _Bin[K, V]] = {}
        self._size = 0
        self._mod_count = 0
        self._initial_capacity = initial_capacity
        if entries is not None:
            items = list(entries.items() if isinstance(entries, Mapping) else entries)
            if items:
                target = math.ceil(len(items) / float(load_factor))
                if target > self._threshold:
                    self._threshold = _table_size_for(target)
                for key, value in items:
                    self.put(key, value)

    @property
    def capacity(self) -> int:
        """Java: HashMap.table length; zero before lazy allocation, for parity diagnostics."""
        return self._capacity

    def _hash(self, key: K) -> int:
        """Java: HashMap#hash; unsigned shift then signed int xor."""
        if isinstance(key, int) and not isinstance(key, bool) and self.key_type != "character":
            bits = 64 if self.key_type == "long" else 32
            if not -(1 << (bits - 1)) <= key < (1 << (bits - 1)):
                raise ValueError(f"Key outside Java {'Long' if bits == 64 else 'Integer'} range")
        h = java_hash_code(key, self.key_type) & 0xFFFFFFFF
        spread = h ^ (h >> 16)
        return spread - (1 << 32) if spread >= 1 << 31 else spread

    def _init_table(self) -> None:
        """Java: HashMap#resize initial lazy allocation."""
        if not self._capacity:
            self._capacity = self._threshold or 16
            self._threshold = self._new_threshold(self._capacity)

    def _new_threshold(self, capacity: int) -> int:
        """Java: HashMap#resize float32 threshold calculation."""
        value = _float32(capacity * self._load_factor)
        return (
            int(value)
            if capacity < _MAXIMUM_CAPACITY and value < _MAXIMUM_CAPACITY
            else (1 << 31) - 1
        )

    def _keys_equal(self, left: K, right: K) -> bool:
        """Java: Character.equals accepts either documented Python code-unit representation."""
        if left is None or right is None:
            return left is right
        if self.key_type == "character":
            return character_hash_code(cast(str | int, left)) == character_hash_code(
                cast(str | int, right)
            )
        return _java_equal(left, right)

    def _find(self, key: K, h: int | None = None) -> _Node[K, V] | None:
        """Java: HashMap#getNode; compare Java equals within the matching bucket."""
        if h is None:
            h = self._hash(key)
        if not self._capacity:
            return None
        bucket = self._table.get(h & (self._capacity - 1))
        if bucket is not None:
            for node in bucket.nodes:
                if node.hash == h and self._keys_equal(key, node.key):
                    return node
        return None

    def __getitem__(self, key: K) -> V:
        """Java: Map#get, with Python Mapping's KeyError for an absent key."""
        node = self._find(key)
        if node is None:
            raise KeyError(key)
        return node.value

    def __contains__(self, key: object) -> bool:
        """Java: HashMap#containsKey (no Python salted hash or numeric key coercion)."""
        return self._find(cast(K, key)) is not None

    def __len__(self) -> int:
        """Java: HashMap#size."""
        return self._size

    def _iteration_nodes(self) -> Iterator[_Node[K, V]]:
        """Java: HashMap.HashIterator#nextNode; table index then next-chain order."""
        for index in sorted(self._table):
            yield from self._table[index].nodes

    def _checked_nodes(self) -> Iterator[_Node[K, V]]:
        """Java: HashMap.HashIterator captures modCount when the iterator is created."""
        expected = self._mod_count
        nodes = list(self._iteration_nodes())

        def iterate() -> Iterator[_Node[K, V]]:
            for node in nodes:
                if not self._concurrent and self._mod_count != expected:
                    raise RuntimeError("Java ConcurrentModificationException")
                yield node

        return iterate()

    def __iter__(self) -> Iterator[K]:
        """Java: HashMap.KeyIterator; structural changes are fail-fast."""
        return (node.key for node in self._checked_nodes())

    def items(self) -> ItemsView[K, V]:
        """Java: HashMap#entrySet; iteration reads values without a LinkedHashMap access."""
        return _JavaItemsView(self)

    def values(self) -> ValuesView[V]:
        """Java: HashMap#values; iteration does not invoke Map#get."""
        return _JavaValuesView(cast(JavaHashMap[object, V], self))

    def _move_root(self, bucket: _Bin[K, V]) -> None:
        """Java: HashMap.TreeNode#moveRootToFront; CHM deliberately does not do this."""
        if not self._concurrent and bucket.root is not None and bucket.nodes[0] is not bucket.root:
            bucket.nodes.remove(bucket.root)
            bucket.nodes.insert(0, bucket.root)

    def _tree_insert(self, bucket: _Bin[K, V], node: _Node[K, V], building: bool = False) -> None:
        """Java: HashMap.TreeNode#putTreeVal / TreeBin#putTreeVal; distinct linked orders."""
        root = bucket.root
        if root is None:
            node.parent = node.left = node.right = None
            node.red = False
            bucket.root = node
            if not building:
                bucket.nodes.append(node)
            return
        parent = root
        while True:
            direction = (node.hash > parent.hash) - (node.hash < parent.hash)
            if not direction:
                direction = _key_compare(node.key, parent.key, self.key_type)
            child = parent.left if direction <= 0 else parent.right
            if child is None:
                node.parent = parent
                node.left = node.right = None
                if direction <= 0:
                    parent.left = node
                else:
                    parent.right = node
                if not building:
                    if self._concurrent:
                        bucket.nodes.insert(0, node)
                    else:
                        bucket.nodes.insert(bucket.nodes.index(parent) + 1, node)
                bucket.root = _balance_insertion(root, node)
                if not building:
                    self._move_root(bucket)
                return
            parent = child

    def _treeify(self, bucket: _Bin[K, V]) -> None:
        """Java: HashMap.TreeNode#treeify / ConcurrentHashMap.TreeBin constructor."""
        bucket.root = None
        for node in bucket.nodes:
            self._tree_insert(bucket, node, building=True)
        self._move_root(bucket)

    def _treeify_bin(self, index: int) -> None:
        """Java: HashMap#treeifyBin; grow small tables before making collision trees."""
        if self._capacity < 64:
            self._resize()
        else:
            self._treeify(self._table[index])

    def _resize(self) -> None:
        """Java: HashMap#resize and TreeNode#split, preserving each relative partition."""
        old_capacity = self._capacity
        if not old_capacity:
            self._init_table()
            return
        if old_capacity >= _MAXIMUM_CAPACITY:
            self._threshold = (1 << 31) - 1
            return
        self._capacity = old_capacity * 2
        self._threshold = (
            self._threshold * 2
            if old_capacity >= 16 and self._capacity < _MAXIMUM_CAPACITY
            else self._new_threshold(self._capacity)
        )
        old_table, self._table = self._table, {}
        for index, bucket in old_table.items():
            low = [n for n in bucket.nodes if not n.hash & old_capacity]
            high = [n for n in bucket.nodes if n.hash & old_capacity]
            for target, nodes, other in [(index, low, high), (index + old_capacity, high, low)]:
                if not nodes:
                    continue
                part = _Bin(nodes)
                self._table[target] = part
                if bucket.root is not None and len(nodes) > 6:
                    if other:
                        self._treeify(part)
                    else:
                        part.root = bucket.root

    def _insert(self, key: K, value: V, *, at_head: bool = False) -> None:
        """Java: HashMap#putVal versus compute/merge's front insertion and resize timing."""
        h = self._hash(key)
        self._init_table()
        index = h & (self._capacity - 1)
        bucket = self._table.setdefault(index, _Bin())
        old_length = len(bucket.nodes)
        node = _Node(h, key, value)
        if bucket.root is not None:
            self._tree_insert(bucket, node)
        else:
            bucket.nodes.insert(0 if at_head else old_length, node)
            if old_length >= (7 if at_head else 8):
                self._treeify_bin(index)
        self._size += 1
        self._mod_count += 1
        if not at_head and self._size > self._threshold:
            self._resize()

    def put(self, key: K, value: V) -> V | None:
        """Java: HashMap#put; return the previous value, or null for a new mapping."""
        node = self._find(key)
        if node is not None:
            previous = node.value
            node.value = value
            self._after_access(node)
            return previous
        self._insert(key, value)
        return None

    def __setitem__(self, key: K, value: V) -> None:
        """Java: HashMap#put with Python's assignment return convention."""
        self.put(key, value)

    def _after_access(self, node: _Node[K, V]) -> None:
        """Java: HashMap#afterNodeAccess; a LinkedHashMap access-order hook."""

    def put_if_absent(self, key: K, value: V) -> V | None:
        """Java: HashMap#putIfAbsent; an existing null value is replaced."""
        node = self._find(key)
        if node is not None and node.value is not None:
            self._after_access(node)
            return node.value
        return self.put(key, value)

    def _prepare_compute(self) -> None:
        """Java: HashMap#computeIfAbsent/#merge grow before lookup, not after insertion."""
        if self._size > self._threshold or not self._capacity:
            self._resize()

    def compute_if_absent(self, key: K, function: Callable[[K], V | None]) -> V | None:
        """Java: HashMap#computeIfAbsent; null results do not create a mapping."""
        if function is None:
            raise ValueError("Java NullPointerException: mapping function")
        self._prepare_compute()
        node = self._find(key)
        if node is not None and node.value is not None:
            self._after_access(node)
            return node.value
        expected = self._mod_count
        value = function(key)
        if expected != self._mod_count:
            raise RuntimeError("Java ConcurrentModificationException in mapping function")
        if value is not None:
            if node is not None:
                node.value = value
                self._after_access(node)
            else:
                self._insert(key, value, at_head=True)
        return value

    def merge(self, key: K, value: V, function: Callable[[V, V], V | None]) -> V | None:
        """Java: HashMap#merge; a null remapping result removes the old mapping."""
        if value is None or function is None:
            raise ValueError("Java NullPointerException: merge value or function")
        self._prepare_compute()
        node = self._find(key)
        if node is None:
            self._insert(key, value, at_head=True)
            return value
        expected = self._mod_count
        result = value if node.value is None else function(node.value, value)
        if expected != self._mod_count:
            raise RuntimeError("Java ConcurrentModificationException in remapping function")
        if result is None:
            self._remove_node(node)
        else:
            node.value = result
            self._after_access(node)
        return result

    def _delete_tree_node(self, bucket: _Bin[K, V], node: _Node[K, V]) -> None:
        """Java: HashMap.TreeNode#removeTreeNode / ConcurrentHashMap.TreeBin#removeTreeNode."""
        root = bucket.root
        assert root is not None
        if not bucket.nodes or root.right is None or root.left is None or root.left.left is None:
            bucket.root = None
            return
        left, right = node.left, node.right
        if left is not None and right is not None:
            successor = right
            while successor.left is not None:
                successor = successor.left
            successor.red, node.red = node.red, successor.red
            sr, parent = successor.right, node.parent
            if successor is right:
                node.parent = successor
                successor.right = node
            else:
                sp = successor.parent
                node.parent = sp
                if sp is not None:
                    if successor is sp.left:
                        sp.left = node
                    else:
                        sp.right = node
                successor.right = right
                right.parent = successor
            node.left = None
            node.right = sr
            if sr is not None:
                sr.parent = node
            successor.left = left
            left.parent = successor
            successor.parent = parent
            if parent is None:
                root = successor
            elif node is parent.left:
                parent.left = successor
            else:
                parent.right = successor
            replacement = sr if sr is not None else node
        elif left is not None:
            replacement = left
        elif right is not None:
            replacement = right
        else:
            replacement = node
        if replacement is not node:
            parent = node.parent
            replacement.parent = parent
            if parent is None:
                root = replacement
                if not self._concurrent:
                    root.red = False
            elif node is parent.left:
                parent.left = replacement
            else:
                parent.right = replacement
            node.left = node.right = node.parent = None
        if not node.red:
            root = _balance_deletion(root, replacement)
        if replacement is node:
            parent = node.parent
            node.parent = None
            if parent is not None:
                if node is parent.left:
                    parent.left = None
                elif node is parent.right:
                    parent.right = None
        bucket.root = root
        self._move_root(bucket)

    def _remove_node(self, node: _Node[K, V]) -> None:
        """Java: HashMap#removeNode; unlink traversal chain before red-black deletion."""
        index = node.hash & (self._capacity - 1)
        bucket = self._table[index]
        bucket.nodes.remove(node)
        if bucket.root is not None:
            self._delete_tree_node(bucket, node)
        if not bucket.nodes:
            del self._table[index]
        self._size -= 1
        self._mod_count += 1

    def __delitem__(self, key: K) -> None:
        """Java: HashMap#remove with Python Mapping's absent-key KeyError."""
        node = self._find(key)
        if node is None:
            raise KeyError(key)
        self._remove_node(node)

    def remove(self, key: K) -> V | None:
        """Java: HashMap#remove; return the former value or null when absent."""
        node = self._find(key)
        if node is None:
            return None
        self._remove_node(node)
        return node.value

    def clear(self) -> None:
        """Java: HashMap#clear retains capacity and increments structural modification count."""
        self._table.clear()
        self._size = 0
        self._mod_count += 1


class JavaConcurrentHashMap[K, V](JavaHashMap[K, V]):
    """Java: ConcurrentHashMap's single-threaded sizing, spreading and iteration order.

    This type does not claim JVM concurrency guarantees. Null keys/values are rejected.
    """

    _concurrent = True

    def __init__(
        self,
        entries: Mapping[K, V] | Iterable[tuple[K, V]] | None = None,
        *,
        initial_capacity: int | None = None,
        load_factor: float = 0.75,
        concurrency_level: int = 1,
        key_type: KeyType | None = None,
    ) -> None:
        """Java: ConcurrentHashMap constructors; initial size includes the load-factor hint."""
        if concurrency_level <= 0:
            raise ValueError("Java concurrencyLevel must be positive")
        super().__init__(
            initial_capacity=initial_capacity, load_factor=load_factor, key_type=key_type
        )
        if initial_capacity is not None:
            target = max(initial_capacity, concurrency_level)
            self._threshold = _table_size_for(int(1.0 + _float32(target / self._load_factor)))
        if entries is not None:
            items = list(entries.items() if isinstance(entries, Mapping) else entries)
            self._threshold = 16
            self._try_presize(len(items))
            for key, value in items:
                self.put(key, value)

    def _hash(self, key: K) -> int:
        """Java: ConcurrentHashMap#spread; unlike HashMap, clear the sign bit."""
        if key is None:
            raise ValueError("Java NullPointerException: ConcurrentHashMap key")
        return super()._hash(key) & 0x7FFFFFFF

    def _new_threshold(self, capacity: int) -> int:
        """Java: ConcurrentHashMap#initTable/transfer always uses a 0.75 resize threshold."""
        return capacity - (capacity >> 2)

    def _try_presize(self, size: int) -> None:
        """Java: ConcurrentHashMap#tryPresize uses size + (size >>> 1) + 1."""
        target = _table_size_for(size + (size >> 1) + 1)
        if not self._capacity:
            self._capacity = max(self._threshold, target)
            self._threshold = self._new_threshold(self._capacity)
        while target > self._threshold and self._capacity < _MAXIMUM_CAPACITY:
            self._resize()

    def _treeify_bin(self, index: int) -> None:
        """Java: ConcurrentHashMap#treeifyBin presizes small tables more aggressively."""
        if self._capacity < 64:
            self._try_presize(self._capacity << 1)
        elif self._table[index].root is None:
            self._treeify(self._table[index])

    def _resize(self) -> None:
        """Java: ConcurrentHashMap#transfer; reverse the prefix preceding each lastRun."""
        old_capacity = self._capacity
        if not old_capacity:
            self._init_table()
            return
        if old_capacity >= _MAXIMUM_CAPACITY:
            return
        self._capacity = old_capacity * 2
        self._threshold = self._new_threshold(self._capacity)
        old_table, self._table = self._table, {}
        for index, bucket in old_table.items():
            low: list[_Node[K, V]] = []
            high: list[_Node[K, V]] = []
            if bucket.root is None:
                run_bit = bucket.nodes[0].hash & old_capacity
                last_run = 0
                for i, node in enumerate(bucket.nodes[1:], 1):
                    bit = node.hash & old_capacity
                    if bit != run_bit:
                        last_run, run_bit = i, bit
                (high if run_bit else low).extend(bucket.nodes[last_run:])
                for node in bucket.nodes[:last_run]:
                    (high if node.hash & old_capacity else low).insert(0, node)
            else:
                low = [n for n in bucket.nodes if not n.hash & old_capacity]
                high = [n for n in bucket.nodes if n.hash & old_capacity]
            for target, nodes, other in [(index, low, high), (index + old_capacity, high, low)]:
                if nodes:
                    part = _Bin(nodes)
                    self._table[target] = part
                    if bucket.root is not None and len(nodes) > 6:
                        if other:
                            self._treeify(part)
                        else:
                            part.root = bucket.root

    def _insert(self, key: K, value: V, *, at_head: bool = False) -> None:
        """Java: ConcurrentHashMap#putVal; append lists, prepend tree nodes, resize at >=."""
        if value is None:
            raise ValueError("Java NullPointerException: ConcurrentHashMap value")
        h = self._hash(key)
        self._init_table()
        index = h & (self._capacity - 1)
        bucket = self._table.setdefault(index, _Bin())
        old_length = len(bucket.nodes)
        node = _Node(h, key, value)
        if bucket.root is not None:
            self._tree_insert(bucket, node)
        else:
            bucket.nodes.append(node)
            if old_length >= 8:
                self._treeify_bin(index)
        self._size += 1
        self._mod_count += 1
        while self._size >= self._threshold and self._capacity < _MAXIMUM_CAPACITY:
            self._resize()

    def _visited_count(self, key: K) -> int:
        """Java: ConcurrentHashMap#putVal/computeIfAbsent/merge binCount before mutation."""
        h = self._hash(key)
        if not self._capacity:
            return 0
        bucket = self._table.get(h & (self._capacity - 1))
        if bucket is None:
            return 0
        if bucket.root is not None:
            return 2
        for i, node in enumerate(bucket.nodes, 1):
            if node.hash == h and self._keys_equal(key, node.key):
                return i
        return len(bucket.nodes)

    def _treeify_after_visit(self, key: K, count: int) -> None:
        """Java: CHM may treeify even when compute returns null or an old value is replaced."""
        if count >= 8:
            self._treeify_bin(self._hash(key) & (self._capacity - 1))

    def put(self, key: K, value: V) -> V | None:
        """Java: ConcurrentHashMap#put rejects null and may treeify a visited existing bin."""
        if value is None:
            raise ValueError("Java NullPointerException: ConcurrentHashMap value")
        count = self._visited_count(key)
        node = self._find(key)
        if node is not None:
            previous = node.value
            node.value = value
            self._treeify_after_visit(key, count)
            return previous
        self._insert(key, value)
        return None

    def put_if_absent(self, key: K, value: V) -> V | None:
        """Java: ConcurrentHashMap#putIfAbsent still traverses/treeifies a non-head old key."""
        if value is None:
            raise ValueError("Java NullPointerException: ConcurrentHashMap value")
        count = self._visited_count(key)
        node = self._find(key)
        if node is not None:
            self._treeify_after_visit(key, count)
            return node.value
        self._insert(key, value)
        return None

    def _prepare_compute(self) -> None:
        """Java: ConcurrentHashMap#computeIfAbsent/#merge initialize before lookup."""
        self._init_table()

    def compute_if_absent(self, key: K, function: Callable[[K], V | None]) -> V | None:
        """Java: CHM#computeIfAbsent can treeify a long bin even if no mapping is added."""
        if function is None:
            raise ValueError("Java NullPointerException: mapping function")
        count = self._visited_count(key)
        self._init_table()
        node = self._find(key)
        if node is not None:
            self._treeify_after_visit(key, count)
            return node.value
        expected = self._mod_count
        value = function(key)
        if expected != self._mod_count:
            raise RuntimeError("Java IllegalStateException: recursive mapping update")
        if value is None:
            self._treeify_after_visit(key, count)
        else:
            self._insert(key, value)
        return value

    def merge(self, key: K, value: V, function: Callable[[V, V], V | None]) -> V | None:
        """Java: CHM#merge treeifies a visited list even on value replacement or removal."""
        count = self._visited_count(key)
        existed = self._find(key) is not None
        result = super().merge(key, value, function)
        if existed:
            self._treeify_after_visit(key, count)
        return result


class JavaLinkedHashMap[K, V](JavaHashMap[K, V]):
    """Java: LinkedHashMap; insertion order by default, optional Java access ordering."""

    def __init__(
        self,
        entries: Mapping[K, V] | Iterable[tuple[K, V]] | None = None,
        *,
        initial_capacity: int | None = None,
        load_factor: float = 0.75,
        key_type: KeyType | None = None,
        access_order: bool = False,
    ) -> None:
        """Java: LinkedHashMap constructors and accessOrder flag."""
        self._order: list[_Node[K, V]] = []
        self._access_order = access_order
        super().__init__(
            entries, initial_capacity=initial_capacity, load_factor=load_factor, key_type=key_type
        )

    def _iteration_nodes(self) -> Iterator[_Node[K, V]]:
        """Java: LinkedHashMap.LinkedHashIterator traverses before/after links."""
        return iter(self._order)

    def _insert(self, key: K, value: V, *, at_head: bool = False) -> None:
        """Java: LinkedHashMap#newNode/newTreeNode appends the independent order chain."""
        super()._insert(key, value, at_head=at_head)
        node = self._find(key)
        assert node is not None
        self._order.append(node)

    def _after_access(self, node: _Node[K, V]) -> None:
        """Java: LinkedHashMap#afterNodeAccess; only moving a non-tail entry modifies order."""
        if self._access_order and self._order and self._order[-1] is not node:
            self._order.remove(node)
            self._order.append(node)
            self._mod_count += 1

    def __getitem__(self, key: K) -> V:
        """Java: LinkedHashMap#get counts as access, unlike entrySet iteration."""
        node = self._find(key)
        if node is None:
            raise KeyError(key)
        self._after_access(node)
        return node.value

    def _remove_node(self, node: _Node[K, V]) -> None:
        """Java: LinkedHashMap#afterNodeRemoval unlinks the independent traversal chain."""
        self._order.remove(node)
        super()._remove_node(node)

    def clear(self) -> None:
        """Java: LinkedHashMap#clear also clears head and tail."""
        self._order.clear()
        super().clear()


class JavaTreeMap[K, V](JavaHashMap[K, V]):
    """Java: TreeMap's natural/comparator order, independent of hash-table traversal."""

    def __init__(
        self,
        entries: Mapping[K, V] | Iterable[tuple[K, V]] | None = None,
        *,
        key_type: KeyType | None = None,
        comparator: Callable[[K, K], int] | None = None,
    ) -> None:
        """Java: TreeMap constructors; comparator equality determines key identity."""
        self._comparator = comparator
        self._sorted_nodes: list[_Node[K, V]] = []
        super().__init__(entries, key_type=key_type)

    def _compare(self, left: K, right: K) -> int:
        """Java: TreeMap#compare; compareTo equality, not Object.equals, identifies a key."""
        if self._comparator is not None:
            return self._comparator(left, right)
        if left is None or right is None:
            raise ValueError("Java NullPointerException: natural-order TreeMap key")
        if self.key_type == "character":
            return _key_compare(left, right, self.key_type)
        if type(left) is not type(right):
            raise TypeError("Java ClassCastException: incompatible TreeMap key classes")
        if isinstance(left, JavaComparable):
            return left.java_compare_to(right)
        return _key_compare(left, right, self.key_type)

    def _position(self, key: K) -> int:
        """Java: TreeMap#getEntry; binary search by the same comparator as the tree."""
        low, high = 0, len(self._sorted_nodes)
        while low < high:
            middle = (low + high) // 2
            if self._compare(key, self._sorted_nodes[middle].key) > 0:
                low = middle + 1
            else:
                high = middle
        return low

    def _find(self, key: K, h: int | None = None) -> _Node[K, V] | None:
        """Java: TreeMap#getEntry uses comparator equality, ignoring hashCode entirely."""
        self._compare(key, key)
        index = self._position(key)
        if index < len(self._sorted_nodes):
            node = self._sorted_nodes[index]
            if self._compare(key, node.key) == 0:
                return node
        return None

    def _insert(self, key: K, value: V, *, at_head: bool = False) -> None:
        """Java: TreeMap#addEntry places a new comparator-distinct key in sorted order."""
        index = self._position(key)
        self._sorted_nodes.insert(index, _Node(0, key, value))
        self._size += 1
        self._mod_count += 1

    def _iteration_nodes(self) -> Iterator[_Node[K, V]]:
        """Java: TreeMap.PrivateEntryIterator traverses ascending comparator order."""
        return iter(self._sorted_nodes)

    def _remove_node(self, node: _Node[K, V]) -> None:
        """Java: TreeMap#deleteEntry removes the comparator-identified entry."""
        self._sorted_nodes.pop(self._position(node.key))
        self._size -= 1
        self._mod_count += 1

    def _prepare_compute(self) -> None:
        """Java: TreeMap default Map computation has no hash-table resize step."""

    def clear(self) -> None:
        """Java: TreeMap#clear."""
        self._sorted_nodes.clear()
        super().clear()


class JavaHashSet[K](MutableSet[K]):
    """Java: HashSet, using the exact backing HashMap constructor and iteration rules."""

    def __init__(
        self,
        elements: Iterable[K] | None = None,
        *,
        initial_capacity: int | None = None,
        load_factor: float = 0.75,
        key_type: KeyType | None = None,
    ) -> None:
        """Java: HashSet()/(int)/(Collection); collection ctor presizes from expected count."""
        values = None if elements is None else list(elements)
        if values is not None and initial_capacity is None:
            initial_capacity = math.ceil(max(len(values), 12) / 0.75)
        self._map: JavaHashMap[K, bool] = JavaHashMap(
            initial_capacity=initial_capacity, load_factor=load_factor, key_type=key_type
        )
        if values is not None:
            for value in values:
                self.add(value)

    def __len__(self) -> int:
        """Java: HashSet#size."""
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        """Java: HashSet#iterator delegates to HashMap.keySet().iterator()."""
        return iter(self._map)

    def __contains__(self, value: object) -> bool:
        """Java: HashSet#contains."""
        return value in self._map

    def add(self, value: K) -> None:
        """Java: HashSet#add with Python MutableSet's return convention."""
        self._map.put(value, True)

    def discard(self, value: K) -> None:
        """Java: HashSet#remove with Python MutableSet's absent-element convention."""
        self._map.remove(value)

    def clear(self) -> None:
        """Java: HashSet#clear."""
        self._map.clear()


class _JavaItemsView[K, V](ItemsView[K, V]):
    """Java: HashMap.EntrySet; live view with next-chain traversal."""

    def __init__(self, mapping: JavaHashMap[K, V]) -> None:
        """Java: HashMap.EntrySet bound to its backing map."""
        super().__init__(mapping)
        self._java_mapping = mapping

    def __contains__(self, value: object) -> bool:
        """Java: EntrySet#contains checks the node directly and does not register access."""
        if not isinstance(value, tuple) or len(value) != 2:
            return False
        node = self._java_mapping._find(value[0])
        return node is not None and _java_equal(node.value, value[1])

    def __iter__(self) -> Iterator[tuple[K, V]]:
        """Java: HashMap.EntryIterator#next."""
        mapping = self._java_mapping
        return ((node.key, node.value) for node in mapping._checked_nodes())


class _JavaValuesView[V](ValuesView[V]):
    """Java: HashMap.Values; live view which does not register accesses."""

    def __init__(self, mapping: JavaHashMap[object, V]) -> None:
        """Java: HashMap.Values bound to its backing map."""
        super().__init__(mapping)
        self._java_mapping = mapping

    def __contains__(self, value: object) -> bool:
        """Java: Values#contains/HashMap#containsValue uses boxed-value equality."""
        return any(_java_equal(value, node.value) for node in self._java_mapping._iteration_nodes())

    def __iter__(self) -> Iterator[V]:
        """Java: HashMap.ValueIterator#next."""
        mapping = self._java_mapping
        return (node.value for node in mapping._checked_nodes())
