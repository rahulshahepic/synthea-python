"""Java: JavaCollectionsProbe; exact Java 21 hashing and collection iteration goldens."""

from __future__ import annotations

import json
import struct
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from synthea.javacompat.collections import (
    JavaConcurrentHashMap,
    JavaHashMap,
    JavaHashSet,
    JavaLinkedHashMap,
    JavaTreeMap,
)
from synthea.javacompat.hashing import (
    JavaCharacter,
    JavaLong,
    _simple_lower,
    _simple_upper,
    arrays_hash_code,
    boolean_hash_code,
    character_hash_code,
    double_hash_code,
    double_to_long_bits,
    integer_hash_code,
    java_sort_key,
    list_hash_code,
    long_hash_code,
    objects_hash,
    string_compare_to,
    string_compare_to_ignore_case,
    string_hash_code,
    utf16_units,
)


def _rows(path: Path) -> Iterator[dict]:
    """Read probe output without replacing or deriving any expected values."""
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def _text(units: list[int]) -> str:
    """Java: String(char[]); preserve unpaired surrogates from probe transport."""
    return b"".join(unit.to_bytes(2, "big") for unit in units).decode("utf-16-be", "surrogatepass")


def _double(bits: str) -> float:
    """Java: Double#longBitsToDouble."""
    return struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]


@pytest.mark.parity
def test_javacompat_hashes_and_string_order(golden: Callable[[str], Path]) -> None:
    """At least 1,000 values per boxed type, plus Objects/Arrays/List and comparisons."""
    count = 0
    for row in _rows(golden("JavaCollectionsProbe") / "hashes.jsonl"):
        text, other = _text(row["string"]), _text(row["other"])
        wide, decimal = int(row["long"]), _double(row["double"])
        actual = [
            string_hash_code(text),
            integer_hash_code(row["integer"]),
            long_hash_code(wide),
            double_hash_code(decimal),
            boolean_hash_code(row["boolean"]),
            character_hash_code(row["character"]),
        ]
        assert actual == row["hashes"], count
        objects = [
            text,
            row["integer"],
            JavaLong(wide),
            decimal,
            row["boolean"],
            JavaCharacter(row["character"]),
            None,
        ]
        assert objects_hash(*objects) == row["objectsHash"], count
        assert arrays_hash_code(objects) == row["arrayHash"], count
        assert list_hash_code(objects) == row["listHash"], count
        assert arrays_hash_code([wide, -1, -(1 << 63)], "long") == row["longArrayHash"], count
        assert arrays_hash_code([decimal, -0.0, float("nan")], "double") == row["doubleArrayHash"]
        assert arrays_hash_code([row["boolean"], True, False], "boolean") == row["booleanArrayHash"]
        assert string_compare_to(text, other) == row["compare"], count
        assert string_compare_to_ignore_case(text, other) == row["compareIgnoreCase"], count
        sign = (java_sort_key(text) > java_sort_key(other)) - (
            java_sort_key(text) < java_sort_key(other)
        )
        assert sign == (row["compare"] > 0) - (row["compare"] < 0), count
        count += 1
    assert count >= 1000


@pytest.mark.parity
def test_javacompat_simple_case_mappings(golden: Callable[[str], Path]) -> None:
    """Java: Character.toUpperCase/toLowerCase for every Unicode code point (JDK 21)."""
    with (golden("JavaCollectionsProbe") / "case-mappings.jsonl").open() as stream:
        changed = {row[0]: row[1:] for line in stream if (row := json.loads(line))}
    for cp in range(0x110000):
        assert [_simple_upper(cp), _simple_lower(cp)] == changed.get(cp, [cp, cp]), hex(cp)


@dataclass(frozen=True)
class _ProbeKey:
    """Java: JavaCollectionsProbe.ProbeKey, a collision-heavy Comparable key."""

    value: int

    def java_hash_code(self) -> int:
        """Java: ProbeKey#hashCode."""
        return self.value % 7

    def java_compare_to(self, other: object) -> int:
        """Java: ProbeKey#compareTo."""
        assert isinstance(other, _ProbeKey)
        return (self.value > other.value) - (self.value < other.value)


@dataclass(frozen=True)
class _SplitKey:
    """Java: JavaCollectionsProbe.SplitKey; hash bits force tree-bin resize splits."""

    value: int

    def java_hash_code(self) -> int:
        """Java: SplitKey#hashCode."""
        return self.value % 7 | (self.value // 7 % 32) << 6

    def java_compare_to(self, other: object) -> int:
        """Java: SplitKey#compareTo."""
        assert isinstance(other, _SplitKey)
        return (self.value > other.value) - (self.value < other.value)


def _decode(key: object, kind: str) -> object:
    """Decode transport values; key semantics remain in the implementation under test."""
    if kind == "string":
        return _text(key)
    if kind == "long":
        return int(key)
    if kind == "double":
        return _double(key)
    if kind == "custom":
        return _ProbeKey(key)
    if kind == "split":
        return _SplitKey(key)
    return key


def _encode(key: object, kind: str) -> object:
    """Same lossless transport as JavaCollectionsProbe#encoded, not an order oracle."""
    if kind == "string":
        return list(utf16_units(key))
    if kind == "long":
        return str(key)
    if kind == "double":
        return format(double_to_long_bits(key), "x")
    if kind in {"custom", "split"}:
        return key.value
    return key


def _build(row: dict) -> JavaHashMap | JavaHashSet:
    """Replay the exact Java constructor, including collection and map presizing."""
    kind, ctor, key_type = row["kind"], row["ctor"], row["keyType"]
    initial = [(_decode(key, key_type), value) for key, value in row["initial"]]
    typed = {"key_type": "object" if key_type in {"custom", "split"} else key_type}
    if kind == "TreeMap":
        if ctor == 3:
            natural = JavaTreeMap(**typed)
            return JavaTreeMap(comparator=lambda a, b: -natural._compare(a, b), **typed)
        return JavaTreeMap(initial if ctor == 2 else None, **typed)
    kwargs = dict(typed)
    if ctor in {1, 3}:
        kwargs["initial_capacity"] = row["capacity"]
    if ctor == 3:
        kwargs["load_factor"] = row["loadFactor"]
        if kind == "ConcurrentHashMap":
            kwargs["concurrency_level"] = row["concurrency"]
        if kind == "LinkedHashMap":
            kwargs["access_order"] = row["accessOrder"]
    if kind == "HashSet":
        return JavaHashSet([key for key, _ in initial] if ctor == 2 else None, **kwargs)
    cls = {
        "HashMap": JavaHashMap,
        "ConcurrentHashMap": JavaConcurrentHashMap,
        "LinkedHashMap": JavaLinkedHashMap,
    }[kind]
    return cls(initial if ctor == 2 else None, **kwargs)


@pytest.mark.parity
def test_javacompat_collection_mutations(golden: Callable[[str], Path]) -> None:
    """256 scenarios per collection; every operation result and ordered snapshot is exact."""
    tree_splits: Counter[str] = Counter()
    counts: Counter[str] = Counter()
    sizes: dict[str, list[int]] = {}
    for row in _rows(golden("JavaCollectionsProbe") / "collections.jsonl"):
        label = f"{row['kind']} scenario {row['id']} ({row['keyType']}, ctor {row['ctor']})"
        collection = _build(row)
        key_type = row["keyType"]

        def snapshot(collection=collection, key_type=key_type) -> list:
            items = (
                ((key, 1) for key in collection)
                if isinstance(collection, JavaHashSet)
                else collection.items()
            )
            return [[_encode(key, key_type), value] for key, value in items]

        assert snapshot() == row["snapshots"]["0"], label + " initial"
        for step, op in enumerate(row["operations"], 1):
            backing = collection._map if isinstance(collection, JavaHashSet) else collection
            capacity_before = backing.capacity
            mixed_tree = capacity_before and any(
                bucket.root is not None
                and any(node.hash & capacity_before for node in bucket.nodes)
                and any(not node.hash & capacity_before for node in bucket.nodes)
                for bucket in backing._table.values()
            )
            name = op[0]
            if name == "clear":
                collection.clear()
                result = None
            else:
                key = _decode(op[1], key_type)
                if isinstance(collection, JavaHashSet):
                    existed = key in collection
                    if name == "put":
                        collection.add(key)
                        result = not existed
                    elif name == "remove":
                        collection.discard(key)
                        result = existed
                    else:
                        result = existed
                elif name == "put":
                    result = collection.put(key, op[2])
                elif name == "remove":
                    result = collection.remove(key)
                elif name == "putIfAbsent":
                    result = collection.put_if_absent(key, op[2])
                elif name == "compute":
                    result = collection.compute_if_absent(key, lambda ignored, v=op[2]: v)
                elif name == "merge":
                    result = collection.merge(
                        key, op[2], lambda a, b, drop=op[3]: None if drop else a + b
                    )
                elif name == "get":
                    result = collection.get(key)
                else:
                    raise AssertionError(name)
            if mixed_tree and backing.capacity > capacity_before:
                tree_splits[row["kind"]] += 1
            assert result == row["returns"][step - 1], f"{label}, op {step}: {op} return"
            if str(step) in row["snapshots"]:
                assert snapshot() == row["snapshots"][str(step)], f"{label}, op {step}: order"
        counts[row["kind"]] += 1
        sizes.setdefault(row["kind"], []).append(len(row["operations"]) - 120)
    assert set(counts) == {"HashMap", "HashSet", "ConcurrentHashMap", "LinkedHashMap", "TreeMap"}
    assert all(count >= 200 for count in counts.values()), counts
    assert all(min(values) == 0 and max(values) == 5000 for values in sizes.values()), sizes

    assert tree_splits["HashMap"] > 0 and tree_splits["ConcurrentHashMap"] > 0, tree_splits
