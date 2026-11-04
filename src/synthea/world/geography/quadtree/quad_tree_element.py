"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/geography/quadtree/QuadTreeElement.java.
"""

from __future__ import annotations

from typing import Protocol


class QuadTreeElement(Protocol):
    """Java: QuadTreeElement; pending T10."""

    def __init__(self) -> None:
        """Java: QuadTreeElement#QuadTreeElement.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QuadTreeElement#QuadTreeElement — pending T10")

    def get_x(self) -> float:
        """Java: QuadTreeElement#getX.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QuadTreeElement#getX — pending T10")

    def get_y(self) -> float:
        """Java: QuadTreeElement#getY.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QuadTreeElement#getY — pending T10")

    def distance(self, element: QuadTreeElement) -> float:
        """Java: QuadTreeElement#distance.

        Java overloads:
        (QuadTreeElement element)
        """
        raise NotImplementedError("Java: QuadTreeElement#distance — pending T10")
