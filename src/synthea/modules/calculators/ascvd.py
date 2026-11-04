"""Java API skeleton: ASCVD.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class ASCVD:
    """Java: ASCVD; pending T23."""

    TEN_YEARS_IN_MS: ClassVar[int] = 315360000000
    ASCVD_COEFFICIENTS: ClassVar[list[list[float]]] = [
        [-29.799, 17.114, 12.344, 2.469],
        [4.884, 0, 0, 0],
        [13.54, 0.94, 11.853, 0.302],
        [-3.114, 0, -2.664, 0],
        [-13.578, -18.92, -7.99, -0.307],
        [3.149, 4.475, 1.769, 0],
        [2.019, 29.291, 1.797, 1.916],
        [0, -6.432, 0, 0],
        [1.957, 27.82, 1.764, 1.809],
        [0, -6.087, 0, 0],
        [7.574, 0.691, 7.837, 0.549],
        [-1.665, 0, -1.795, 0],
        [0.661, 0.874, 0.658, 0.645],
        [-29.18, 86.61, 61.18, 19.54],
        [0.9665, 0.9533, 0.9144, 0.8954],
    ]

    def __init__(self) -> None:
        """Java: ASCVD#ASCVD.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ASCVD#ASCVD — pending T23")

    @staticmethod
    def ascvd10_year(person: Person, time: int, per_timestep: bool) -> float:
        """Java: ASCVD#ascvd10Year.

        Java overloads:
        (Person person, long time, boolean perTimestep)
        """
        raise NotImplementedError("Java: ASCVD#ascvd10Year — pending T23")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: ASCVD#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: ASCVD#inventoryAttributes — pending T23")
