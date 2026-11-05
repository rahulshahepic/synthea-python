"""Java: JDK 21 HashMap/HashSet/ConcurrentHashMap and boxed/string edge contracts."""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass

import pytest

from synthea.javacompat.collections import (
    JavaConcurrentHashMap,
    JavaHashMap,
    JavaHashSet,
    JavaLinkedHashMap,
    JavaTreeMap,
    NondeterministicJavaOrderError,
)
from synthea.javacompat.hashing import (
    JavaCharacter,
    JavaLong,
    arrays_hash_code,
    character_hash_code,
    double_hash_code,
    java_hash_code,
    java_sort_key,
    list_hash_code,
    objects_hash,
    string_compare_to,
    string_compare_to_ignore_case,
    string_hash_code,
)


def test_boxed_hashes_and_null_array_rules() -> None:
    """Java: boxed hashCode, Objects.hash and Arrays.hashCode null/empty distinctions."""
    assert string_hash_code("Aa") == string_hash_code("BB") == 2112
    assert string_hash_code("abc") == 96354
    assert java_hash_code(None) == 0
    assert java_hash_code(1 << 32, "integer") == 0
    assert java_hash_code(1 << 32, "long") == 1
    assert java_hash_code(True) == 1231 and java_hash_code(False) == 1237
    assert arrays_hash_code(None) == 0
    assert arrays_hash_code([]) == list_hash_code([]) == objects_hash() == 1
    assert objects_hash("abc") == 31 + string_hash_code("abc")
    assert objects_hash(JavaLong(1 << 32)) == 32
    assert objects_hash(JavaCharacter("A")) == 31 + 65
    with pytest.raises(TypeError):
        java_hash_code(object())


def test_surrogates_character_and_string_order() -> None:
    """Java: String stores UTF-16 units, while Character cannot contain a whole astral point."""
    assert string_hash_code("🚀") == string_hash_code("\ud83d\ude80")
    assert string_compare_to("🚀", "\ud83d\ude80") == 0
    assert string_compare_to("𐀀", "\ue000") == 0xD800 - 0xE000
    assert sorted(["\ue000", "𐀀"], key=java_sort_key) == ["𐀀", "\ue000"]
    assert character_hash_code("\ud800") == 0xD800
    assert character_hash_code(0xFFFF) == 0xFFFF
    for invalid in ["", "ab", "🚀", -1, 65536]:
        with pytest.raises(ValueError):
            character_hash_code(invalid)


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("I", "ı", 0),
        ("İ", "i", 0),
        ("Σ", "ς", 0),
        ("𐐀", "𐐨", 0),
        ("ß", "SS", ord("ß") - ord("s")),
        ("BB", "🚀", ord("b") - 0xD83D),
        ("abc", "AB", 1),
    ],
)
def test_simple_case_comparison(left: str, right: str, expected: int) -> None:
    """Java: String#compareToIgnoreCase uses simple case mappings and coder-specific scans."""
    assert string_compare_to_ignore_case(left, right) == expected


def test_double_hash_and_key_identity() -> None:
    """Java: Double.equals canonicalizes NaNs but distinguishes +0.0 and -0.0."""
    other_nan = struct.unpack(">d", bytes.fromhex("fff123456789abcd"))[0]
    assert math.isnan(other_nan)
    assert double_hash_code(other_nan) == double_hash_code(float("nan"))
    assert double_hash_code(-0.0) == -(1 << 31)
    assert double_hash_code(0.0) == 0
    mapping = JavaHashMap[float, int](key_type="double")
    mapping[-0.0] = 1
    mapping[0.0] = 2
    mapping[float("nan")] = 3
    mapping[other_nan] = 4
    assert len(mapping) == 3
    assert mapping[-0.0] == 1 and mapping[0.0] == 2 and mapping[other_nan] == 4


def test_numeric_boxed_key_types_do_not_collapse() -> None:
    """Java: Boolean, Integer, Long and Character remain different key classes."""
    mapping = JavaHashMap[object, str]()
    for key, value in [
        (True, "boolean"),
        (1, "integer"),
        (JavaLong(1), "long"),
        (JavaCharacter(1), "character"),
        (1.0, "double"),
    ]:
        mapping[key] = value
    assert len(mapping) == 5
    assert mapping[True] == "boolean" and mapping[1] == "integer"
    assert mapping[JavaLong(1)] == "long" and mapping[1.0] == "double"
    longs = JavaHashMap[int, str](key_type="long")
    longs[-(1 << 63)] = "minimum"
    assert longs[-(1 << 63)] == "minimum"
    with pytest.raises(ValueError):
        JavaHashMap[int, int]()[1 << 32] = 1


def test_utf16_equivalent_string_keys_are_equal() -> None:
    """Java: String#equals sees the same code-unit sequence for either Python spelling."""
    mapping = JavaHashMap[str, int]()
    mapping["🚀"] = 1
    assert mapping.put("\ud83d\ude80", 2) == 1
    assert len(mapping) == 1 and mapping["🚀"] == 2


def test_null_values_and_computation_resize_timing() -> None:
    """Java: HashMap compute/merge pre-resize and front-insert instead of put's tail rule."""
    mapping = JavaHashMap[str | None, int | None](initial_capacity=2)
    mapping[None] = None
    assert None in mapping and mapping.put_if_absent(None, 4) is None
    assert mapping[None] == 4
    assert mapping.compute_if_absent("x", lambda _: None) is None and "x" not in mapping
    assert mapping.capacity == 2
    assert mapping.compute_if_absent("x", lambda _: 3) == 3
    assert mapping.capacity == 2  # unlike put, compute does not immediately grow at size 2
    assert mapping.compute_if_absent("x", lambda _: 9) == 3
    assert mapping.capacity == 4  # pre-resize happens even though the key already exists
    assert mapping.merge("x", 2, lambda a, b: a + b) == 5
    assert mapping.merge("x", 2, lambda a, b: None) is None and "x" not in mapping
    with pytest.raises(ValueError):
        mapping.merge("x", None, lambda a, b: 0)


def test_iterator_captures_modification_count_at_creation() -> None:
    """Java: HashMap.HashIterator captures expectedModCount in its constructor."""
    mapping = JavaHashMap[str, int]({"a": 1})
    iterator = iter(mapping)
    mapping["b"] = 2
    with pytest.raises(RuntimeError, match="ConcurrentModification"):
        next(iterator)
    iterator = iter(mapping.items())
    mapping["a"] = 7  # value replacement is not a structural change
    assert dict(iterator)["a"] == 7


def test_reentrant_hashmap_computation_is_detected() -> None:
    """Java: HashMap#computeIfAbsent rejects structural updates from the callback."""
    mapping = JavaHashMap[str, int]()

    def reenter(_: str) -> int:
        mapping["other"] = 2
        return 1

    with pytest.raises(RuntimeError, match="ConcurrentModification"):
        mapping.compute_if_absent("key", reenter)
    assert "key" not in mapping and mapping["other"] == 2


@pytest.mark.parametrize("method", ["put", "put_if_absent"])
def test_concurrent_map_null_rejection(method: str) -> None:
    """Java: ConcurrentHashMap rejects null regardless of an existing key/value."""
    mapping = JavaConcurrentHashMap[str | None, int | None]()
    mapping["a"] = 1
    with pytest.raises(ValueError, match="NullPointer"):
        getattr(mapping, method)(None, 1)
    with pytest.raises(ValueError, match="NullPointer"):
        getattr(mapping, method)("a", None)
    with pytest.raises(ValueError, match="NullPointer"):
        mapping.get(None)


def test_linked_hashmap_access_order_and_views() -> None:
    """Java: LinkedHashMap.get moves an entry, entrySet/values iteration does not."""
    mapping = JavaLinkedHashMap[str, int]([("a", 1), ("b", 2), ("c", 3)], access_order=True)
    assert list(mapping.items()) == [("a", 1), ("b", 2), ("c", 3)]
    assert list(mapping.values()) == [1, 2, 3]
    assert list(mapping) == ["a", "b", "c"]
    assert mapping["a"] == 1
    assert list(mapping) == ["b", "c", "a"]
    iterator = iter(mapping)
    mapping.get("b")
    with pytest.raises(RuntimeError):
        next(iterator)
    mapping.remove("c")
    assert list(mapping) == ["a", "b"]


@dataclass(frozen=True)
class _CollisionKey:
    """Java: a deterministic Comparable key with intentionally constant hashCode."""

    value: int

    def java_hash_code(self) -> int:
        return 42

    def java_compare_to(self, other: object) -> int:
        assert isinstance(other, _CollisionKey)
        return (self.value > other.value) - (self.value < other.value)


@pytest.mark.parametrize("cls", [JavaHashMap, JavaConcurrentHashMap])
def test_tree_invariants_through_insertion_resize_and_removal(cls: type[JavaHashMap]) -> None:
    """Java: TreeNode/TreeBin balancing, including root promotion and untreeification."""
    mapping = cls(initial_capacity=64, key_type="object")

    def check() -> None:
        for bucket in mapping._table.values():
            if bucket.root is None:
                continue
            assert not bucket.root.red and bucket.root.parent is None
            assert len(bucket.nodes) == len({id(node) for node in bucket.nodes})

            def height(node) -> int:
                if node is None:
                    return 1
                if node.left is not None:
                    assert node.left.parent is node
                if node.right is not None:
                    assert node.right.parent is node
                if node.red:
                    assert node.left is None or not node.left.red
                    assert node.right is None or not node.right.red
                left, right = height(node.left), height(node.right)
                assert left == right
                return left + (not node.red)

            height(bucket.root)

    for index in range(80):
        mapping[_CollisionKey(index)] = index
        check()
    assert any(bucket.root is not None for bucket in mapping._table.values())
    for index in [*range(0, 80, 2), *range(1, 80, 2)]:
        assert mapping.remove(_CollisionKey(index)) == index
        check()
    assert not mapping and not mapping._table


def test_custom_noncomparable_tree_identity_is_explicit() -> None:
    """Java: TreeNode.tieBreakOrder is nondeterministic without supplied Java identity."""

    @dataclass(frozen=True)
    class Key:
        value: int

        def java_hash_code(self) -> int:
            return 1

    mapping = JavaHashMap[Key, int](initial_capacity=64)
    with pytest.raises(NondeterministicJavaOrderError, match="identityHashCode"):
        for index in range(12):
            mapping[Key(index)] = index


def test_treemap_comparator_identity_and_no_hash_requirement() -> None:
    """Java: TreeMap comparison determines equality and never requires hashCode."""
    mapping = JavaTreeMap[str, int](comparator=string_compare_to_ignore_case)
    mapping["A"] = 1
    assert mapping.put("a", 2) == 1
    assert list(mapping.items()) == [("A", 2)]

    @dataclass(frozen=True)
    class ComparableOnly:
        value: int

        def java_compare_to(self, other: object) -> int:
            assert isinstance(other, ComparableOnly)
            return (self.value > other.value) - (self.value < other.value)

    natural = JavaTreeMap[ComparableOnly, int]()
    for index in [9, 0, 3, 1]:
        natural[ComparableOnly(index)] = index
    assert list(natural.values()) == [0, 1, 3, 9]
    assert natural.remove(ComparableOnly(3)) == 3
    with pytest.raises(ValueError, match="NullPointer"):
        JavaTreeMap().get(None)


def test_set_collection_constructor_counts_duplicates_for_presizing() -> None:
    """Java: HashSet(Collection) presizes by input collection size, not its distinct size."""
    duplicates = JavaHashSet([True] * 100)
    assert len(duplicates) == 1 and duplicates._map.capacity == 256
    duplicates.add(False)
    duplicates.discard(True)
    assert list(duplicates) == [False]
    duplicates.clear()
    assert not duplicates and duplicates._map.capacity == 256


def test_character_key_representations_and_view_membership() -> None:
    """Java: Character keys and boxed equality in entrySet/values without access reordering."""
    characters = JavaHashMap[str | int, int](key_type="character")
    characters["A"] = 7
    assert characters[65] == 7
    assert characters.put(65, 8) == 7 and len(characters) == 1
    linked = JavaLinkedHashMap[str, object]([("a", 1), ("b", True)], access_order=True)
    assert ("a", 1) in linked.items()
    assert ("b", 1) not in linked.items()
    assert list(linked) == ["a", "b"]
    assert True in JavaHashMap({"a": True}).values()
    assert 1 not in JavaHashMap({"a": True}).values()


@pytest.mark.parametrize("cls", [JavaHashMap, JavaConcurrentHashMap, JavaTreeMap])
def test_null_callbacks_rejected_even_for_an_existing_mapping(cls: type[JavaHashMap]) -> None:
    """Java: computeIfAbsent/merge requireNonNull callbacks before taking the old-value path."""
    mapping = cls({"a": 1})
    with pytest.raises(ValueError, match="NullPointer"):
        mapping.compute_if_absent("a", None)
    with pytest.raises(ValueError, match="NullPointer"):
        mapping.merge("missing", 3, None)


def test_character_null_key_in_a_treeified_bin() -> None:
    """Java: HashMap<Character, V> permits null alongside char zero during treeification."""
    mapping = JavaHashMap[int | None, int](initial_capacity=64, key_type="character")
    mapping[None] = -1
    for value in range(0, 1280, 64):
        mapping[value] = value
    assert mapping[None] == -1 and mapping[0] == 0
    assert mapping.remove(None) == -1
    assert 0 in mapping and None not in mapping
