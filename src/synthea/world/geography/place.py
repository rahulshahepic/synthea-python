"""Named postal places. Java: org.mitre.synthea.world.geography.Place."""

from __future__ import annotations

from synthea.javacompat.hashing import string_compare_to_ignore_case
from synthea.world.agents.person import Point2DDouble
from synthea.world.geography.quadtree.quad_tree_element import QuadTreeElement


class Place(QuadTreeElement):
    """Java: org.mitre.synthea.world.geography.Place."""

    def __init__(self, row: dict[str, str]) -> None:
        """Java: Place#Place."""
        self.state: str = row["USPS"]
        self.abbreviation: str = row["ST"]
        self.name: str = row["NAME"]
        self.postal_code: str = row["ZCTA5"]
        self.coordinate: Point2DDouble = Point2DDouble(float(row["LON"]), float(row["LAT"]))

    def same_state(self, state: str) -> bool:
        """Java: Place#sameState."""
        return (
            string_compare_to_ignore_case(self.state, state) == 0
            or string_compare_to_ignore_case(self.abbreviation, state) == 0
        )

    def get_x(self) -> float:
        """Java: Place#getX."""
        return self.coordinate.get_x()

    def get_y(self) -> float:
        """Java: Place#getY."""
        return self.coordinate.get_y()
