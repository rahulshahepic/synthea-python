"""Ports of Java QuadTreeTest, retaining its million-element workload per case."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from synthea.javacompat.random import JavaRandom
from synthea.world.geography.quadtree.quad_tree import QuadTree
from synthea.world.geography.quadtree.quad_tree_element import QuadTreeElement


@dataclass(slots=True)
class Element(QuadTreeElement):
    """Java: QuadTreeTest.TestElement; concrete coordinates and default distance."""

    x: float
    y: float

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y


@pytest.mark.parametrize("quadrant", [None, 0, 1, 2, 3])
def test_geography_quadtree_upstream_million_insertions(quadrant: int | None) -> None:
    """Java: testInsertOneMillionElements and testInsertNE/NW/SE/SW."""
    random = JavaRandom(0)
    tree = QuadTree()
    amount = 1_000_000
    for _ in range(amount):
        x, y = random.next_double(), random.next_double()
        if quadrant is None:
            x, y = x * 360.0 - 180.0, y * 360.0 - 180.0
        else:
            x *= -180.0 if quadrant in (1, 3) else 180.0
            y *= -180.0 if quadrant in (2, 3) else 180.0
        assert tree.insert(Element(x, y))
    assert not tree.is_leaf
    assert tree.size() == amount
    if quadrant is not None:
        assert amount == len(tree.data) + tree.branches[quadrant].size()
        assert all(branch.is_leaf for i, branch in enumerate(tree.branches) if i != quadrant)


def test_geography_quadtree_upstream_million_tightly_packed_queries() -> None:
    """Java: QuadTreeTest#testQueryAgainstOneMillionTightlyPackedElements."""
    random = JavaRandom(0)
    tree = QuadTree()
    amount = 1_000_000
    for _ in range(amount):
        assert tree.insert(
            Element(random.next_double() * 10.0 - 5.0, random.next_double() * 10.0 - 5.0)
        )
    assert not tree.is_leaf
    assert tree.size() == amount
    query = Element(0, 0)
    radius = 0.125
    while radius <= 2.0:
        results = tree.query(query, radius)
        assert results
        assert all(query.distance(item) <= radius for item in results)
        radius *= 2.0
