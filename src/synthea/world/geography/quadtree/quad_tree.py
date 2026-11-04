"""Java API skeleton: QuadTree.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.geography.quadtree.quad_tree_element import QuadTreeElement


class QuadTree:
    """Java: QuadTree; pending T10."""

    def __init__(
        self, x: float | None = None, y: float | None = None, r: float | None = None
    ) -> None:
        """Java: QuadTree#QuadTree.

        Java overloads:
        ()
        (double x, double y, double r)
        """
        self.is_leaf: bool
        self.max_leaf_size: int
        self.data: list[QuadTreeElement]
        self.xcoord: float
        self.ycoord: float
        self.radius: float
        self.branches: list[QuadTree]
        raise NotImplementedError("Java: QuadTree#QuadTree — pending T10")

    def has_bounds_around(self, item: QuadTreeElement, error: float | None = None) -> bool:
        """Java: QuadTree#hasBoundsAround.

        Java overloads:
        (QuadTreeElement item)
        (QuadTreeElement item, double error)
        """
        raise NotImplementedError("Java: QuadTree#hasBoundsAround — pending T10")

    def insert(self, item: QuadTreeElement) -> bool:
        """Java: QuadTree#insert.

        Java overloads:
        (QuadTreeElement item)
        """
        raise NotImplementedError("Java: QuadTree#insert — pending T10")

    def query(self, query_point: QuadTreeElement, radius: float) -> list[QuadTreeElement]:
        """Java: QuadTree#query.

        Java overloads:
        (QuadTreeElement queryPoint, double radius)
        """
        raise NotImplementedError("Java: QuadTree#query — pending T10")

    def size(self) -> int:
        """Java: QuadTree#size.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QuadTree#size — pending T10")

    def to_string(self) -> str:
        """Java: QuadTree#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QuadTree#toString — pending T10")
