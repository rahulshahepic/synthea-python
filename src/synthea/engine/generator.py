"""Java API skeleton for generator.py.
Java: org.mitre.synthea.engine.Generator.
"""

from __future__ import annotations


class Generator:
    """Java: Generator; pending T27."""

    DEFAULT_STATE: str = "Massachusetts"
    TARGET_AGE: str = "target_age"
    ANSI_GREEN: str = "\u001B[32m"
    ANSI_BLUE: str = "\u001B[34m"
    ANSI_RESET: str = "\u001B[0m"
    DONATION_LINK: str = "https://github.com/sponsors/synthetichealth"
    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Generator constructor; pending T27."""
        self.id: object = None
        self.options: object = None
        self.populationRandom: object = None
        self.clinicianRandom: object = None
        self.timestep: int = 0
        self.stop: int = 0
        self.referenceTime: int = 0
        self.stats: str | None = None
        self.location: object = None
        self.totalGeneratedPopulation: object = None
        self.logLevel: str | None = None
        self.onlyAlivePatients: bool = False
        self.onlyDeadPatients: bool = False
        self.onlyVeterans: bool = False
        self.keepPatientsModule: object = None
        self.maxAttemptsToKeepPatient: object = None
        self.exporterRuntimeOptions: object = None
        self.threadPoolSize: int = 0
        self.population: int = 0
        self.endTime: int = 0
        self.runStartTime: int = 0
        self.seed: int = 0
        self.clinicianSeed: int = 0
        self.singlePersonSeed: object = None
        self.overflow: bool = False
        self.gender: str | None = None
        self.ageSpecified: bool = False
        self.minAge: int = 0
        self.maxAge: int = 0
        self.city: str | None = None
        self.state: str | None = None
        self.localModuleDir: object = None
        self.fixedRecordPath: object = None
        self.enabledModules: str | None = None
        self.initialPopulationSnapshotPath: object = None
        self.updatedPopulationSnapshotPath: object = None
        self.daysToTravelForward: int = 0
        self.keepPatientsModulePath: object = None
        self.rejectDeadButOverflow: bool = False
        self.isAliveButDeadRequired: bool = False
        self.isDeadButAliveRequired: bool = False
        self.insufficientProviders: bool = False
        self.failedKeepModule: bool = False
        raise NotImplementedError("Java: Generator — pending T27")

    def get_module_predicate(self, *args: object, **kwargs: object) -> object:
        """Java: Generator#getModulePredicate."""
        raise NotImplementedError("Java: getModulePredicate — pending T27")

    def get_randomizer(self, *args: object, **kwargs: object) -> object:
        """Java: Generator#getRandomizer."""
        raise NotImplementedError("Java: getRandomizer — pending T27")

    def birthdate_from_target_age(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#birthdate_from_target_age."""
        raise NotImplementedError("Java: birthdate_from_target_age — pending T27")

    def check_criteria(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#check_criteria."""
        raise NotImplementedError("Java: check_criteria — pending T27")

    def create_person(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#create_person."""
        raise NotImplementedError("Java: create_person — pending T27")

    def export_anyway(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#export_anyway."""
        raise NotImplementedError("Java: export_anyway — pending T27")

    def generate_person(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#generate_person."""
        raise NotImplementedError("Java: generate_person — pending T27")

    def get_module_names(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#get_module_names."""
        raise NotImplementedError("Java: get_module_names — pending T27")

    def init(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#init."""
        raise NotImplementedError("Java: init — pending T27")

    def meets_criteria(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#meets_criteria."""
        raise NotImplementedError("Java: meets_criteria — pending T27")

    def pick_demographics(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#pick_demographics."""
        raise NotImplementedError("Java: pick_demographics — pending T27")

    def pick_fixed_demographics(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#pick_fixed_demographics."""
        raise NotImplementedError("Java: pick_fixed_demographics — pending T27")

    def random_demographics(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#random_demographics."""
        raise NotImplementedError("Java: random_demographics — pending T27")

    def record_person(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#record_person."""
        raise NotImplementedError("Java: record_person — pending T27")

    def run(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#run."""
        raise NotImplementedError("Java: run — pending T27")

    def update_person(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#update_person."""
        raise NotImplementedError("Java: update_person — pending T27")

    def update_record_export_person(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#update_record_export_person."""
        raise NotImplementedError("Java: update_record_export_person — pending T27")

    def write_to_console(self, *args: object, **kwargs: object) -> object:
        """Java: generator.py#write_to_console."""
        raise NotImplementedError("Java: write_to_console — pending T27")


class GeneratorOptions:
    """Java: Generator#GeneratorOptions; pending T27."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Generator#GeneratorOptions constructor."""
        raise NotImplementedError("Java: GeneratorOptions — pending T27")


class CriteriaCheck:
    """Java: Generator#CriteriaCheck; pending T27."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Generator#CriteriaCheck constructor."""
        raise NotImplementedError("Java: CriteriaCheck — pending T27")
