"""Java: org.mitre.synthea.world.geography.quadtree.QuadTree."""

from __future__ import annotations

from synthea.javacompat.fmt import double_to_string
from synthea.world.geography.quadtree.quad_tree_element import QuadTreeElement


class QuadTree:
    """Java: QuadTree; splitting retains existing data in its parent."""

    def __init__(
        self, x: float | None = None, y: float | None = None, r: float | None = None
    ) -> None:
        """Java: QuadTree#QuadTree."""
        self.is_leaf: bool = True
        self.max_leaf_size: int = 50
        self.data: list[QuadTreeElement] = []
        self.xcoord: float = 0.0 if x is None else x
        self.ycoord: float = 0.0 if y is None else y
        self.radius: float = 180.0 if r is None else r
        self.branches: list[QuadTree] = []

    def has_bounds_around(self, item: QuadTreeElement, error: float | None = None) -> bool:
        """Java: QuadTree#hasBoundsAround."""
        error = 0.0 if error is None else error
        return (
            self.xcoord + self.radius >= item.get_x() - error
            and self.xcoord - self.radius <= item.get_x() + error
            and self.ycoord + self.radius >= item.get_y() - error
            and self.ycoord - self.radius <= item.get_y() + error
        )

    def insert(self, item: QuadTreeElement) -> bool:
        """Java: QuadTree#insert."""
        if self.is_leaf:
            if len(self.data) < self.max_leaf_size:
                self.data.append(item)
                return True
            self.is_leaf = False
            d = self.radius / 2.0
            self.branches = [
                QuadTree(self.xcoord + dx, self.ycoord + dy, d)
                for dx, dy in ((d, d), (-d, d), (d, -d), (-d, -d))
            ]
            return self.insert(item)
        for branch in self.branches:
            if branch.has_bounds_around(item) and branch.insert(item):
                return True
        self.data.append(item)
        return True

    def query(self, query_point: QuadTreeElement, radius: float) -> list[QuadTreeElement]:
        """Java: QuadTree#query."""
        results = [item for item in self.data if query_point.distance(item) <= radius]
        if not self.is_leaf:
            for branch in self.branches:
                if branch.has_bounds_around(query_point, radius):
                    results.extend(branch.query(query_point, radius))
        return results

    def size(self) -> int:
        """Java: QuadTree#size."""
        return len(self.data) + sum(branch.size() for branch in self.branches)

    def to_string(self) -> str:
        """Java: QuadTree#toString."""
        kind = "Leaf" if self.is_leaf else "Branch"
        coords = ", ".join(double_to_string(v) for v in (self.xcoord, self.ycoord, self.radius))
        return f"{kind} @ ({coords}) = {self.size()}"
