"""Test doubles for T20 component tests (tests/ only, AGENTS.md §4).

`create_encounter_double` stands in for `EncounterModule.createEncounter`
(T22, still a stub) in component tests. It implements only the
state/RNG plumbing the Java method performs — reserve the current
encounter slot, start the encounter on the real HealthRecord, attach
the code, assign a real provider and clinician through the real
Person/Provider code — so module logic that reads encounter state
follows the same path it follows in Java. Provider selection and
clinician choice use the production implementations (T09/T14), not
doubles. EncounterModule's own behaviour (when encounters happen,
immunizations, costs) is not modelled; that is T22's integration
surface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.helpers.utilities import Utilities
from synthea.modules.encounter_module import EncounterModule
from synthea.world.agents.provider import Provider
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code, Encounter, EncounterType


def create_encounter_double(
    person: Person,
    time: int,
    type: EncounterType,
    specialty: str,
    code: Code,
    module: str,
) -> Encounter | None:
    """Double for EncounterModule#createEncounter (pending T22).

    Mirrors the Java method's plumbing: no new encounter while one is
    active, reserve the slot, encounterStart, attach the code, assign
    provider (first loaded provider for cardiology, otherwise the
    person's provider for the type), increment the provider's
    encounter count, and choose a clinician from the provider's list.
    """
    if person.has_current_encounter():
        return None
    year = Utilities.get_year(time)
    person.reserve_current_encounter(time, module)
    encounter = person.encounter_start(time, type)
    if code is not None:
        encounter.codes.append(code)
    if specialty is None:
        # Java: specialty.equalsIgnoreCase(...) on null raises NPE.
        raise TypeError("Java: NullPointerException (specialty is null)")
    if specialty.upper() == ClinicianSpecialty.CARDIOLOGY.upper():
        prov = Provider.get_provider_list()[0]
    else:
        prov = person.get_provider(type, time)
    prov.increment_encounters(type, year)
    encounter.provider = prov
    encounter.clinician = prov.choose_clinician_list(specialty, person)
    return encounter


def install_create_encounter_double() -> None:
    """Replace the T22 stub with the double (component tests only)."""
    EncounterModule.create_encounter = staticmethod(create_encounter_double)  # type: ignore[method-assign]


def remove_create_encounter_double(original: object) -> None:
    """Restore the original create_encounter (the T22 stub)."""
    EncounterModule.create_encounter = original  # type: ignore[method-assign]
