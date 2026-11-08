"""Java: org.mitre.synthea.modules.CardiovascularDiseaseModule."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from synthea.engine.module import Module
from synthea.helpers.utilities import Utilities
from synthea.modules.calculators.ascvd import ASCVD, Inventory, _inventory
from synthea.modules.calculators.framingham import Framingham

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code


class CardiovascularDiseaseModule(Module):
    """Java: CardiovascularDiseaseModule; annual risk attributes for generic modules."""

    useFramingham: ClassVar[bool] = False
    tenYearsInMS: ClassVar[int] = 315360000000
    oneMonthInMS: ClassVar[int] = 2592000000

    def __init__(self) -> None:
        """Java: CardiovascularDiseaseModule#CardiovascularDiseaseModule."""
        super().__init__()
        self.name = "Cardiovascular Disease"

    def clone(self) -> Module:
        """Java: CardiovascularDiseaseModule#clone returns the stateless module itself."""
        return self

    def process(self, person: Person, time: int) -> bool:  # type: ignore[override]
        """Java: CardiovascularDiseaseModule#process (the declared two-argument overload)."""
        if not person.alive(time):
            return True
        if self.useFramingham:
            self.calculate_cardio_risk(person, time)
        else:
            self.calculate_ascvd_risk(person, time)
        self.calculate_atrial_fibrillation_risk(person, time)
        self.calculate_stroke_risk(person, time)
        return False

    @staticmethod
    def calculate_cardio_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateCardioRisk."""
        risk = Framingham.chd10_year(person, time, False)
        person.attributes["framingham_risk"] = risk
        CardiovascularDiseaseModule._store_risk(person, risk)

    @staticmethod
    def calculate_ascvd_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateAscvdRisk."""
        risk = ASCVD.ascvd10_year(person, time, False)
        person.attributes["ascvd_risk"] = risk
        CardiovascularDiseaseModule._store_risk(person, risk)

    @staticmethod
    def _store_risk(person: Person, risk: float) -> None:
        """Java: common statements in calculateCardioRisk/calculateAscvdRisk."""
        c = CardiovascularDiseaseModule
        person.attributes["cardio_risk"] = Utilities.convert_risk_to_timestep(risk, c.tenYearsInMS)
        monthly = Utilities.convert_risk_to_timestep(risk, c.tenYearsInMS, c.oneMonthInMS)
        person.attributes["mi_risk"] = monthly
        person.attributes["ihd_risk"] = monthly * 5

    @staticmethod
    def calculate_atrial_fibrillation_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateAtrialFibrillationRisk."""
        risk = Framingham.atrial_fibrillation10_year(person, time, False)
        person.attributes["atrial_fibrillation_risk"] = Utilities.convert_risk_to_timestep(
            risk, CardiovascularDiseaseModule.tenYearsInMS
        )

    @staticmethod
    def calculate_stroke_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateStrokeRisk."""
        risk = Framingham.stroke10_year(person, time, False)
        person.attributes["stroke_risk"] = Utilities.convert_risk_to_timestep(
            risk, CardiovascularDiseaseModule.tenYearsInMS
        )

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: CardiovascularDiseaseModule#getAllCodes."""
        return []

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: CardiovascularDiseaseModule#inventoryAttributes."""
        for key in (
            "ascvd_risk",
            "atrial_fibrillation_risk",
            "cardio_risk",
            "framingham_risk",
            "ihd_risk",
            "mi_risk",
            "stroke_risk",
        ):
            _inventory(attributes, "CardiovascularDiseaseModule", key, False, True, "0.001")
