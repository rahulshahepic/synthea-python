"""Java API skeleton: Place.java."""

from __future__ import annotations


class Place:
    """Java: Place; pending T10."""

    def __init__(self, row: dict[str, str]) -> None:
        """Java: Place#Place.

        Java overloads:
        (Map row)
        """
        self.state: str
        self.abbreviation: str
        self.name: str
        self.postal_code: str
        self.coordinate: float
        raise NotImplementedError("Java: Place#Place — pending T10")

    def same_state(self, state: str) -> bool:
        """Java: Place#sameState.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: Place#sameState — pending T10")

    def get_x(self) -> float:
        """Java: Place#getX.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Place#getX — pending T10")

    def get_y(self) -> float:
        """Java: Place#getY.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Place#getY — pending T10")
