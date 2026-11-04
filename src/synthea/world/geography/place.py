"""Java port skeleton: java/src/main/java/org/mitre/synthea/world/geography/Place.java."""

from __future__ import annotations


class Place:
    """Java: org.mitre.synthea.world.geography.Place; pending T10."""

    state: str
    abbreviation: str
    name: str
    postal_code: str
    coordinate: tuple[float, float]

    def __init__(self, row: dict[str, str]) -> None:
        """Java: Place#Place(Map<String,String> row); pending T10."""
        self.state: str = ""
        self.abbreviation: str = ""
        self.name: str = ""
        self.postalCode: str = ""
        self.coordinate: tuple[float, float] = (0.0, 0.0)
        raise NotImplementedError("Java: Place#constructor — pending T10")

    def same_state(self, state: str) -> bool:
        """Java: Place#sameState(String state); pending T10."""
        raise NotImplementedError("Java: Place#sameState — pending T10")

    def get_x(self) -> float:
        """Java: Place#getX(); pending T10."""
        raise NotImplementedError("Java: Place#getX — pending T10")

    def get_y(self) -> float:
        """Java: Place#getY(); pending T10."""
        raise NotImplementedError("Java: Place#getY — pending T10")
