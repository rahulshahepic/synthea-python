"""Java: org.mitre.synthea.engine.Generator, single-threaded population generation."""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol, cast
from uuid import UUID, uuid4

from synthea.engine.module import Module
from synthea.export.exporter import Exporter, ExporterRuntimeOptions
from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.numbers import d2i, d2l, parse_long, to_int32, to_int64
from synthea.modules.death_module import DeathModule
from synthea.modules.encounter_module import EncounterModule
from synthea.modules.health_insurance_module import HealthInsuranceModule
from synthea.modules.lifecycle_module import LifecycleModule
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.agents.provider import Provider
from synthea.world.concepts.costs import Costs
from synthea.world.concepts.health_record import EncounterType
from synthea.world.geography.location import Location

if TYPE_CHECKING:
    from synthea.world.geography.demographics import Demographics


class Entity(Protocol):
    """Java boundary: identity.Entity (fixed records out of scope)."""


class EntityManager(Protocol):
    """Java boundary: identity.EntityManager (fixed records out of scope)."""


class AtomicInteger:
    """Java: AtomicInteger value surface; generation is single-threaded in this port."""

    def __init__(self, value: int = 0) -> None:
        """Java: AtomicInteger#AtomicInteger."""
        self.value = to_int32(value)

    def get(self) -> int:
        """Java: AtomicInteger#get."""
        return self.value

    def increment_and_get(self) -> int:
        """Java: AtomicInteger#incrementAndGet."""
        self.value = to_int32(self.value + 1)
        return self.value

    def __int__(self) -> int:
        """Java: AtomicInteger#intValue."""
        return self.value


class GeneratorOptions:
    """Java: Generator.GeneratorOptions default parameter object."""

    def __init__(self) -> None:
        """Java: GeneratorOptions#GeneratorOptions field initializers."""
        self.population = Config.get_as_integer("generate.default_population", 1)
        self.thread_pool_size = Config.get_as_integer("generate.thread_pool_size", -1)
        self.reference_time = int(time.time() * 1000)
        self.end_time = self.reference_time
        self.run_start_time = self.reference_time
        self.seed = self.reference_time
        self.clinician_seed = self.reference_time
        self.single_person_seed: int | None = None
        self.overflow = True
        self.gender: str | None = None
        self.age_specified = False
        self.min_age = 0
        self.max_age = 140
        self.city: str | None = None
        self.state: str | None = None
        self.local_module_dir: Path | None = None
        self.fixed_record_path: Path | None = None
        self.enabled_modules: list[str] | None = None
        self.initial_population_snapshot_path: Path | None = None
        self.updated_population_snapshot_path: Path | None = None
        self.days_to_travel_forward = -1
        self.keep_patients_module_path: Path | None = None


class CriteriaCheck:
    """Java: Generator.CriteriaCheck cached criteria flags."""

    def __init__(self) -> None:
        """Java: CriteriaCheck#CriteriaCheck, default false fields."""
        self.reject_dead_but_overflow = False
        self.is_alive_but_dead_required = False
        self.is_dead_but_alive_required = False
        self.insufficient_providers = False
        self.failed_keep_module = False

    def meets_criteria(self) -> bool:
        """Java: CriteriaCheck#meetsCriteria."""
        return not (
            self.reject_dead_but_overflow
            or self.is_alive_but_dead_required
            or self.is_dead_but_alive_required
            or self.insufficient_providers
            or self.failed_keep_module
        )

    def export_anyway(self) -> bool:
        """Java: CriteriaCheck#exportAnyway; overflow alone still exports dead patients."""
        return not (
            self.is_alive_but_dead_required
            or self.is_dead_but_alive_required
            or self.insufficient_providers
            or self.failed_keep_module
        )


class Generator:
    """Java: Generator; preserves serial Java seed, retry and timestep order."""

    DEFAULT_STATE: ClassVar[str] = "Massachusetts"
    entityManager: ClassVar[EntityManager | None] = None
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
        seed_or_ero: int | ExporterRuntimeOptions | None = None,
        clinician_seed: int | None = None,
    ) -> None:
        """Java: Generator#Generator overloads, including the int overload's second init."""
        self.id: UUID = uuid4()
        self.options = (
            population_or_o if isinstance(population_or_o, GeneratorOptions) else GeneratorOptions()
        )
        self.exporter_runtime_options = (
            seed_or_ero
            if isinstance(seed_or_ero, ExporterRuntimeOptions)
            else ExporterRuntimeOptions()
        )
        self.internal_store: list[Person] | None = None
        self.keep_patients_module: Module | None = None
        self._check_scope()
        if self.options.thread_pool_size != -1 and self.options.thread_pool_size <= 0:
            raise ValueError(f"Illegal thread pool size ({self.options.thread_pool_size})")
        self.thread_pool_size = 1
        self.init()
        if isinstance(population_or_o, int):
            self.options.population = population_or_o
            if isinstance(seed_or_ero, int):
                if clinician_seed is None:
                    raise TypeError("Generator(int,long,long) requires clinician_seed")
                self.options.seed = seed_or_ero
                self.options.clinician_seed = clinician_seed
            self.init()

    def _check_scope(self) -> None:
        """Java: Generator optional snapshot, fixed-record, filter and editor paths."""
        for value, label in [
            (self.options.initial_population_snapshot_path, "population snapshots"),
            (self.options.updated_population_snapshot_path, "population snapshots"),
            (self.options.fixed_record_path, "fixed records"),
            (self.options.keep_patients_module_path, "keep-patients"),
        ]:
            if value is not None:
                raise NotImplementedError(f"{label} are out of scope")
        if self.entityManager is not None:
            raise NotImplementedError("fixed records are out of scope")
        if Config.get_as_boolean("growtherrors", False):
            raise NotImplementedError("growth-data error editors are out of scope")
        if Config.get_as_boolean("exporter.cdw.export", False):
            raise NotImplementedError("CDW exporter is out of scope")

    def init(self) -> None:
        """Java: Generator#init; real provider/payer/module initialization."""
        self._check_scope()
        if self.options.state is None:
            self.options.state = self.DEFAULT_STATE
        Location.get_index(self.options.state)
        Exporter.load_custom_exporters()
        Exporter.load_code_mappers()
        self.population_random = DefaultRandomNumberGenerator(self.options.seed)
        self.clinician_random = DefaultRandomNumberGenerator(self.options.clinician_seed)
        self.timestep = parse_long(cast(str, Config.get("generate.timestep")))
        self.stop = self.options.end_time
        self.reference_time = self.options.reference_time
        self.location = Location(self.options.state, self.options.city)
        self.log_level = Config.get("generate.log_patients.detail", "simple")
        self.only_dead_patients = Config.get_as_boolean("generate.only_dead_patients")
        self.only_alive_patients = Config.get_as_boolean("generate.only_alive_patients")
        if self.only_dead_patients and self.only_alive_patients:
            Config.set("generate.only_dead_patients", "false")
            Config.set("generate.only_alive_patients", "false")
            self.only_dead_patients = self.only_alive_patients = False
        try:
            maximum = parse_long(
                cast(str, Config.get("generate.max_attempts_to_keep_patient", "1000"))
            )
            self.max_attempts_to_keep_patient: int | None = maximum if maximum != 0 else None
        except (ValueError, TypeError):
            self.max_attempts_to_keep_patient = None
        self.only_veterans = Config.get_as_boolean("generate.veteran_population_override")
        self.total_generated_population = AtomicInteger()
        self.stats = {"alive": AtomicInteger(), "dead": AtomicInteger()}
        self.module_predicate = self.get_module_predicate()
        Provider.load_providers(self.location, self.clinician_random)
        PayerManager.load_payers(self.location)
        if self.options.local_module_dir is not None:
            Module.add_modules(self.options.local_module_dir)
        core_names = self.get_module_names(Module.get_modules(lambda _: False))
        names = self.get_module_names(Module.get_modules(self.module_predicate))
        Costs.load_cost_data()
        location_name = (
            self.options.state
            if self.options.city is None
            else self.options.city + ", " + self.options.state
        )
        print(
            f"Running with options:\nPopulation: {self.options.population}\nSeed: {self.options.seed}\nProvider Seed:{self.options.clinician_seed}\nReference Time: {self.options.reference_time}\nLocation: {location_name}"
        )
        print(f"Min Age: {self.options.min_age}\nMax Age: {self.options.max_age}")
        if self.options.gender is not None:
            print(f"Gender: {self.options.gender}")
        if self.options.enabled_modules is not None:
            names = sorted((n for n in names if n not in core_names), key=str.lower)
            print("Modules: " + "\n       & ".join(names))
            print(f"       > [{len(names)} loaded]")

    def get_module_names(self, modules: list[Module]) -> list[str]:
        """Java: Generator#getModuleNames."""
        return [m.name for m in modules]

    def run(self) -> None:
        """Java: Generator#run, Java one-worker submission order without thread scheduling."""
        self._check_scope()
        if self.options.single_person_seed is None:
            seeds = [self.population_random.rand_long() for _ in range(self.options.population)]
            for index, seed in enumerate(seeds):
                self.generate_person(index, seed)
        else:
            self.generate_person(0, self.options.single_person_seed)
        Exporter.run_post_completion_exports(self, self.exporter_runtime_options)
        total = self.total_generated_population.get()
        print(
            f"Records: total={total}, alive={self.stats['alive'].get()}, dead={self.stats['dead'].get()}"
        )
        print(
            f"RNG={self.population_random.get_count()}\nClinician RNG={self.clinician_random.get_count()}"
        )
        print(
            f"\n{self.ANSI_GREEN}You've just generated {total} patients!{self.ANSI_RESET} We're happy to know Synthea is helping you with your project."
        )
        print(
            "Like what we're doing? Synthea is an open-source project, and your support helps us keep building."
        )
        print(
            f"Please consider {self.ANSI_BLUE}{self.FORMATTED_DONATION_LINK}{self.ANSI_RESET} ({self.DONATION_LINK}).\n"
        )

    def generate_person(self, index: int, person_seed: int | None = None) -> Person:
        """Java: Generator#generatePerson; demographics persist across failed/dead attempts."""
        if person_seed is None:
            person_seed = (uuid4().int >> 64) & ((1 << 63) - 1)
        person = Person(person_seed)
        if self.entityManager is not None:
            raise NotImplementedError("fixed records are out of scope")
        demographics = self.random_demographics(cast(RandomNumberGenerator, person))
        attempt = 0
        while True:
            attempt += 1
            person = self.create_person(person_seed, demographics)
            finish = person.last_updated + self.timestep
            alive = person.alive(finish)
            check = self.check_criteria(person, finish, index, alive)
            meets = check.meets_criteria()
            if not meets:
                if (
                    self.max_attempts_to_keep_patient is not None
                    and attempt >= self.max_attempts_to_keep_patient
                ):
                    raise RuntimeError(
                        f"Failed to produce a matching patient after {attempt} attempts. "
                        "Ensure that it is possible for all requested demographics to meet the criteria. "
                        "(e.g., make sure there is no age restriction that conflicts with a requested condition, "
                        "such as limiting age to 0-18 and requiring all patients have a condition that only onsets after 55.) "
                        "If you are confident that the constraints are possible to satisfy but rare, "
                        "consider increasing the value in config setting `generate.max_attempts_to_keep_patient`"
                    )
                if not check.export_anyway():
                    person_seed = person.rand_long()
                    continue
            self.record_person(person, index)
            if not alive:
                person_seed = person.rand_long()
                if (
                    attempt > 10
                    and cast(int, person.attributes[self.TARGET_AGE]) > 90
                    and (not self.options.age_specified or self.options.min_age <= 85)
                ):
                    target = person.rand_int(5) + 85
                    demographics[self.TARGET_AGE] = target
                    demographics[Person.BIRTHDATE] = self.birthdate_from_target_age(
                        target, cast(RandomNumberGenerator, person)
                    )
            exported = Exporter.export(person, finish, self.exporter_runtime_options)
            if not exported:
                person_seed = person.rand_long()
                demographics = self.random_demographics(cast(RandomNumberGenerator, person))
            if meets and exported:
                return person

    def check_criteria(
        self, person: Person, finish_time: int, index: int, is_alive: bool
    ) -> CriteriaCheck:
        """Java: Generator#checkCriteria."""
        check = CriteriaCheck()
        check.reject_dead_but_overflow = (
            not is_alive and not self.only_dead_patients and self.options.overflow
        )
        check.is_alive_but_dead_required = is_alive and self.only_dead_patients
        check.is_dead_but_alive_required = not is_alive and self.only_alive_patients
        check.insufficient_providers = person.provider_count() < 1
        if self.keep_patients_module is not None:
            raise NotImplementedError("keep-patients filters are out of scope")
        return check

    def update_record_export_person(self, person: Person, index: int) -> Person:
        """Java: Generator#updateRecordExportPerson."""
        self.update_person(person)
        self.record_person(person, index)
        Exporter.export(person, person.last_updated + self.timestep, self.exporter_runtime_options)
        return person

    def create_person(self, person_seed: int, demo_attributes: dict[str, object]) -> Person:
        """Java: Generator#createPerson; real birth, social determinants and module list."""
        person = Person(person_seed)
        person.population_seed = self.options.seed
        person.attributes.update(demo_attributes)
        person.attributes[Person.LOCATION] = self.location
        person.last_updated = cast(int, demo_attributes[Person.BIRTHDATE])
        self.location.set_social_determinants(person)
        LifecycleModule.birth(person, person.last_updated)
        person.current_modules = Module.get_modules(self.module_predicate)
        self.update_person(person)
        return person

    def update_person(self, person: Person) -> None:
        """Java: Generator#updatePerson, preserving update/removal/closing/death order."""
        insurance = HealthInsuranceModule()
        encounter_module = EncounterModule()
        current = person.last_updated
        while person.alive(current) and current < self.stop:
            if person.attributes.get(Person.ENTITY) is not None:
                raise NotImplementedError("fixed records are out of scope")
            insurance.process(person, current)
            encounter_module.process(person, current)
            assert person.current_modules is not None
            remaining = []
            for module in person.current_modules:
                if not module.process(person, current):
                    remaining.append(module)
            person.current_modules[:] = remaining
            encounter_module.end_encounter_module_encounters(person, current)
            person.last_updated = current
            # Growth-data editors are disabled in the CSV-only port; no editors are registered.
            if Config.get_as_boolean("growtherrors", False):
                raise NotImplementedError("growth-data error editors are out of scope")
            current += self.timestep
        if person.has_current_encounter():
            assert person.record is not None
            end = person.last_updated
            previous = person.record.current_encounter(self.stop)
            kind = EncounterType.from_string(previous.type)
            if kind in (EncounterType.INPATIENT, EncounterType.HOSPICE, EncounterType.SNF):
                end = self.stop
            if Person.DEATHDATE in person.attributes:
                end = min(end, cast(int, person.attributes[Person.DEATHDATE]))
            person.record.encounter_end(end, kind)
        DeathModule.process(person, current)

    def random_demographics(self, random: RandomNumberGenerator) -> dict[str, object]:
        """Java: Generator#randomDemographics."""
        return self.pick_demographics(random, self.location.random_city(random))

    def write_to_console(self, person: Person, index: int, time: int, is_alive: bool) -> None:
        """Java: Generator#writeToConsole simple and detailed output."""
        a = person.attributes
        deceased = "" if is_alive else "DECEASED"
        print(
            f"{index + 1} -- {a.get(Person.NAME)} ({person.age_in_years(time)} y/o {a.get(Person.GENDER)}) {a.get(Person.CITY)}, {a.get(Person.STATE)} {deceased} ({person.get_count()})"
        )
        if self.log_level == "detailed":
            print("ATTRIBUTES")
            for key, value in a.items():
                print(f"  * {key} = {value}")
            print(f"SYMPTOMS: {person.symptom_total()}")
            assert person.record is not None
            print(person.record.text_summary())
            print("VITAL SIGNS")
            for sign in person.vital_signs:
                print(f"  * {sign!s:>25} = {person.get_vital_sign(sign, time):6.2f}")
            print("-----")

    def pick_demographics(
        self, random: RandomNumberGenerator, city: Demographics
    ) -> dict[str, object]:
        """Java: Generator#pickDemographics; all draws and HashMap insertions in Java order."""
        result: dict[str, object] = cast(dict[str, object], JavaHashMap[str, object]())
        result[Person.CITY], result[Person.STATE], result[Person.COUNTY] = (
            city.city,
            city.state,
            city.county,
        )
        race = city.pick_race(random)
        result[Person.RACE] = race
        ethnicity = city.pick_ethnicity(random)
        result[Person.ETHNICITY] = ethnicity
        result[Person.FIRST_LANGUAGE] = city.language_from_race_and_ethnicity(
            race, ethnicity, random
        )
        if self.options.gender is not None:
            gender = self.options.gender
        else:
            gender = city.pick_gender(random)
            gender = "M" if gender.lower() in ("male", "m") else "F"
        result[Person.GENDER] = gender
        education = city.pick_education(random)
        result[Person.EDUCATION] = education
        education_level = city.education_level(education, random)
        result[Person.EDUCATION_LEVEL] = education_level
        income = city.pick_income(random)
        result[Person.INCOME] = income
        income_level = city.income_level(income)
        result[Person.INCOME_LEVEL] = income_level
        result[Person.POVERTY_RATIO] = city.poverty_ratio(income)
        occupation = cast(float, random.rand())
        result[Person.OCCUPATION_LEVEL] = occupation
        score = city.socioeconomic_score(income_level, education_level, occupation)
        result[Person.SOCIOECONOMIC_SCORE] = score
        result[Person.SOCIOECONOMIC_CATEGORY] = city.socioeconomic_category(score)
        if self.only_veterans:
            result["veteran_population_override"] = True
        age = (
            d2i(
                self.options.min_age
                + ((self.options.max_age - self.options.min_age) * cast(float, random.rand()))
            )
            if self.options.age_specified
            else city.pick_age(random)
        )
        result[self.TARGET_AGE] = age
        result[Person.BIRTHDATE] = self.birthdate_from_target_age(age, random)
        return result

    def pick_fixed_demographics(
        self, entity: Entity, random: RandomNumberGenerator
    ) -> dict[str, object]:
        """Java: Generator#pickFixedDemographics, issue-excluded identity path."""
        raise NotImplementedError("fixed records are out of scope")

    def birthdate_from_target_age(self, target_age: int, random: RandomNumberGenerator) -> int:
        """Java: Generator#birthdateFromTargetAge, double addition before truncating long."""
        earliest = to_int64(
            self.reference_time - to_int64(to_int64(to_int64(target_age + 1) * 365 + 1) * 86400000)
        )
        latest = to_int64(self.reference_time - to_int64(to_int64(target_age * 365) * 86400000))
        return d2l(float(earliest) + (to_int64(latest - earliest) * cast(float, random.rand())))

    def record_person(self, person: Person, index: int) -> None:
        """Java: Generator#recordPerson, before destructive export and retry RNG draws."""
        finish = person.last_updated + self.timestep
        alive = person.alive(finish)
        if self.internal_store is not None:
            self.internal_store.append(person)
        if self.log_level != "none":
            self.write_to_console(person, index, finish, alive)
        self.stats["alive" if alive else "dead"].increment_and_get()
        self.total_generated_population.increment_and_get()

    def get_module_predicate(self) -> Callable[[str], bool]:
        """Java: Generator#getModulePredicate; Commons IO case-insensitive * and ? wildcards."""
        if self.options.enabled_modules is None:
            return lambda _: True
        patterns = [
            re.compile(
                re.escape(p).replace(r"\*", ".*").replace(r"\?", "."), re.IGNORECASE | re.DOTALL
            )
            for p in self.options.enabled_modules
        ]
        return lambda path: any(p.fullmatch(path) is not None for p in patterns)

    def get_randomizer(self) -> RandomNumberGenerator:
        """Java: Generator#getRandomizer."""
        return cast(RandomNumberGenerator, self.population_random)


setattr(Generator, "GeneratorOptions", GeneratorOptions)  # noqa: B010
setattr(Generator, "CriteriaCheck", CriteriaCheck)  # noqa: B010
