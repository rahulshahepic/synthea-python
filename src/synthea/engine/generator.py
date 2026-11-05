"""Java API skeleton: Generator.java."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.export.exporter import ExporterRuntimeOptions as ExporterExporterRuntimeOptions
    from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.person import Person
    from synthea.world.geography.demographics import Demographics
    from synthea.world.geography.location import Location

    class AtomicInteger(Protocol):
        """Java boundary type: AtomicInteger; external to the mapped Python port."""

    class Entity(Protocol):
        """Java boundary type: Entity; external to the mapped Python port."""

    class EntityManager(Protocol):
        """Java boundary type: EntityManager; external to the mapped Python port."""


class Generator:
    """Java: Generator; pending T27."""

    DEFAULT_STATE: ClassVar[str] = "Massachusetts"
    entityManager: ClassVar[EntityManager]  # Java initialization deferred to T27.
    TARGET_AGE: ClassVar[str] = "target_age"
    ANSI_GREEN: ClassVar[str] = "\x1b[32m"
    ANSI_BLUE: ClassVar[str] = "\x1b[34m"
    ANSI_RESET: ClassVar[str] = "\x1b[0m"
    DONATION_LINK: ClassVar[str] = "https://github.com/sponsors/synthetichealth"
    FORMATTED_DONATION_LINK: ClassVar[str] = (
        "\x1b]8;;https://github.com/sponsors/synthetichealth\x07making a donation\x1b]8;;\x07"
    )

    def __init__(
        self,
        population_or_o: int | GeneratorOptions | None = None,
        seed_or_ero: int | ExporterExporterRuntimeOptions | None = None,
        clinician_seed: int | None = None,
    ) -> None:
        """Java: Generator#Generator.

        Java overloads:
        ()
        (int population)
        (int population, long seed, long clinicianSeed)
        (GeneratorOptions o)
        (GeneratorOptions o, Exporter.ExporterRuntimeOptions ero)
        """
        self.id: UUID
        self.options: GeneratorOptions
        self.population_random: DefaultRandomNumberGenerator
        self.clinician_random: DefaultRandomNumberGenerator
        self.timestep: int
        self.stop: int
        self.reference_time: int
        self.stats: dict[str, AtomicInteger]
        self.location: Location
        self.total_generated_population: AtomicInteger
        self.log_level: str
        self.only_alive_patients: bool
        self.only_dead_patients: bool
        self.only_veterans: bool
        self.keep_patients_module: Module
        self.max_attempts_to_keep_patient: int
        self.exporter_runtime_options: ExporterExporterRuntimeOptions
        self.thread_pool_size: int
        self.internal_store: list[Person]
        self.module_predicate: Callable[[str], bool]
        raise NotImplementedError("Java: Generator#Generator — pending T27")

    def init(self) -> None:
        """Java: Generator#init.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Generator#init — pending T27")

    def get_module_names(self, modules: list[Module]) -> list[str]:
        """Java: Generator#getModuleNames.

        Java overloads:
        (List modules)
        """
        raise NotImplementedError("Java: Generator#getModuleNames — pending T27")

    def run(self) -> None:
        """Java: Generator#run.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Generator#run — pending T27")

    def generate_person(self, index: int, person_seed: int | None = None) -> Person:
        """Java: Generator#generatePerson.

        Java overloads:
        (int index)
        (int index, long personSeed)
        """
        raise NotImplementedError("Java: Generator#generatePerson — pending T27")

    def check_criteria(
        self, person: Person, finish_time: int, index: int, is_alive: bool
    ) -> CriteriaCheck:
        """Java: Generator#checkCriteria.

        Java overloads:
        (Person person, long finishTime, int index, boolean isAlive)
        """
        raise NotImplementedError("Java: Generator#checkCriteria — pending T27")

    def update_record_export_person(self, person: Person, index: int) -> Person:
        """Java: Generator#updateRecordExportPerson.

        Java overloads:
        (Person person, int index)
        """
        raise NotImplementedError("Java: Generator#updateRecordExportPerson — pending T27")

    def create_person(self, person_seed: int, demo_attributes: dict[str, object]) -> Person:
        """Java: Generator#createPerson.

        Java overloads:
        (long personSeed, Map demoAttributes)
        """
        raise NotImplementedError("Java: Generator#createPerson — pending T27")

    def update_person(self, person: Person) -> None:
        """Java: Generator#updatePerson.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: Generator#updatePerson — pending T27")

    def random_demographics(self, random: RandomNumberGenerator) -> dict[str, object]:
        """Java: Generator#randomDemographics.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Generator#randomDemographics — pending T27")

    def write_to_console(self, person: Person, index: int, time: int, is_alive: bool) -> None:
        """Java: Generator#writeToConsole.

        Java overloads:
        (Person person, int index, long time, boolean isAlive)
        """
        raise NotImplementedError("Java: Generator#writeToConsole — pending T27")

    def pick_demographics(
        self, random: RandomNumberGenerator, city: Demographics
    ) -> dict[str, object]:
        """Java: Generator#pickDemographics.

        Java overloads:
        (RandomNumberGenerator random, Demographics city)
        """
        raise NotImplementedError("Java: Generator#pickDemographics — pending T27")

    def pick_fixed_demographics(
        self, entity: Entity, random: RandomNumberGenerator
    ) -> dict[str, object]:
        """Java: Generator#pickFixedDemographics.

        Java overloads:
        (Entity entity, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Generator#pickFixedDemographics — pending T27")

    def birthdate_from_target_age(self, target_age: int, random: RandomNumberGenerator) -> int:
        """Java: Generator#birthdateFromTargetAge.

        Java overloads:
        (long targetAge, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Generator#birthdateFromTargetAge — pending T27")

    def record_person(self, person: Person, index: int) -> None:
        """Java: Generator#recordPerson.

        Java overloads:
        (Person person, int index)
        """
        raise NotImplementedError("Java: Generator#recordPerson — pending T27")

    def get_module_predicate(self) -> Callable[[str], bool]:
        """Java: Generator#getModulePredicate.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Generator#getModulePredicate — pending T27")

    def get_randomizer(self) -> RandomNumberGenerator:
        """Java: Generator#getRandomizer.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Generator#getRandomizer — pending T27")


class GeneratorOptions:
    """Java: GeneratorOptions; pending T27."""

    def __init__(self) -> None:
        """Java: GeneratorOptions#GeneratorOptions.

        Java overloads:
        ()
        """
        self.population: int
        self.thread_pool_size: int
        self.reference_time: int
        self.end_time: int
        self.run_start_time: int
        self.seed: int
        self.clinician_seed: int
        self.single_person_seed: int
        self.overflow: bool
        self.gender: str
        self.age_specified: bool
        self.min_age: int
        self.max_age: int
        self.city: str
        self.state: str
        self.local_module_dir: Path
        self.fixed_record_path: Path
        self.enabled_modules: list[str]
        self.initial_population_snapshot_path: Path
        self.updated_population_snapshot_path: Path
        self.days_to_travel_forward: int
        self.keep_patients_module_path: Path
        raise NotImplementedError("Java: GeneratorOptions#GeneratorOptions — pending T27")


class CriteriaCheck:
    """Java: CriteriaCheck; pending T27."""

    def __init__(self) -> None:
        """Java: CriteriaCheck#CriteriaCheck.

        Java overloads:
        ()
        """
        self.reject_dead_but_overflow: bool
        self.is_alive_but_dead_required: bool
        self.is_dead_but_alive_required: bool
        self.insufficient_providers: bool
        self.failed_keep_module: bool
        raise NotImplementedError("Java: CriteriaCheck#CriteriaCheck — pending T27")

    def meets_criteria(self) -> bool:
        """Java: CriteriaCheck#meetsCriteria.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CriteriaCheck#meetsCriteria — pending T27")

    def export_anyway(self) -> bool:
        """Java: CriteriaCheck#exportAnyway.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CriteriaCheck#exportAnyway — pending T27")


setattr(Generator, "GeneratorOptions", GeneratorOptions)  # noqa: B010
setattr(Generator, "CriteriaCheck", CriteriaCheck)  # noqa: B010
