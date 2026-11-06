"""Java: org.mitre.synthea.world.geography.quadtree.QuadTreeElement."""

from __future__ import annotations

import math
from typing import Protocol


class QuadTreeElement(Protocol):
    """Java: QuadTreeElement; structural coordinates and default Euclidean distance."""

    def get_x(self) -> float:
        """Java: QuadTreeElement#getX."""
        ...

    def get_y(self) -> float:
        """Java: QuadTreeElement#getY."""
        ...

    def distance(self, element: QuadTreeElement) -> float:
        """Java: QuadTreeElement#distance."""
        dx = self.get_x() - element.get_x()
        dy = self.get_y() - element.get_y()
        return math.sqrt(dx * dx + dy * dy)
