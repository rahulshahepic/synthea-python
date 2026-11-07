"""Java: org.mitre.synthea.engine.Module (T19).

Module represents the entry point of a generic module. The ``modules``
registry is loaded once per process and shared between the generated
population; ModuleSupplier.get() always returns a clone, so the master
copies stay clean.

Registry notes for the port: Java keys the registry in a TreeMap, so
every read below iterates keys in sorted (Java String.compareTo) order;
for the ASCII module paths in the resources tree that is plain sorted
order. Java's five "core" modules are hand-written Java classes owned
by later tasks (T21/T23 and the COVID module task); their Python
counterparts are still stubs, so the registry holds name-only Module
shells for them (see docs/porting_notes/T19.md).
"""

from __future__ import annotations

import json
import re
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar, cast

from synthea.engine.state import State, Terminal
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.resources import resource_path
from synthea.world.agents.person import Person

# Java core modules: (registry key, name set by the Java constructor,
# Python class that will own it once ported, owning task note).
_CORE_MODULES: list[tuple[str, str, str]] = [
    ("Lifecycle", "Lifecycle", "LifecycleModule (pending T21)"),
    (
        "Cardiovascular Disease",
        "Cardiovascular Disease",
        "CardiovascularDiseaseModule (pending T23)",
    ),
    ("Quality Of Life", "Quality of Life", "QualityOfLifeModule (pending T23)"),
    ("Weight Loss", "Weight Loss", "WeightLossModule (pending T23)"),
    (
        "COVID-19 Immunization Module",
        "COVID-19 Immunization Module",
        "C19ImmunizationModule (pending, covid package)",
    ),
]


def _metrics_enabled() -> bool:
    """Java: TransitionMetrics.enabled (config-gated, default false)."""
    return Config.get_as_boolean("generate.track_detailed_transition_metrics", False)


def _transition_metrics_enter(module: str, state: str, first_time: bool) -> None:
    """Java: TransitionMetrics#enter — a no-op unless enabled by config.

    There is no Python TransitionMetrics module yet (it is not in
    docs/port_map.toml); enabling the flag is out of scope (PORTING_GUIDE
    §8) rather than silently ignored.
    """
    if _metrics_enabled():
        raise NotImplementedError("TransitionMetrics is out of scope for the Python port")


def _transition_metrics_exit(module: str, state: str, destination: str, duration: int) -> None:
    """Java: TransitionMetrics#exit — a no-op unless enabled by config."""
    if _metrics_enabled():
        raise NotImplementedError("TransitionMetrics is out of scope for the Python port")


def _jsonpath_set(data: object, json_path: str, value: float) -> None:
    """Minimal Jayway JsonPath ``set`` for definite paths ($.a.b, $.a[0].b,
    $['a'].b), creating intermediate objects the way JsonPath does."""
    tokens: list[str | int] = []
    for match in re.finditer(r"\.([^.\[\]]+)|\[(\d+)\]|\['([^']*)'\]", json_path):
        if match.group(1) is not None:
            tokens.append(match.group(1))
        elif match.group(2) is not None:
            tokens.append(int(match.group(2)))
        else:
            tokens.append(match.group(3))
    if not tokens:
        return
    current: object = data
    for token in tokens[:-1]:
        if isinstance(current, dict):
            key = cast(str, token)
            child = current.get(key)
            if not isinstance(child, (dict, list)):
                child = {}
                current[key] = child
            current = child
        elif isinstance(current, list) and isinstance(token, int):
            current = current[token]
        else:
            return
    last = tokens[-1]
    if isinstance(current, dict):
        current[cast(str, last)] = value
    elif isinstance(current, list) and isinstance(last, int):
        current[last] = value


class Module:
    """Java: Module."""

    GMF_VERSION: ClassVar[float] = 2.0
    # Java's JSON_PATH_CONFIG (Jayway JsonPath on Gson) has no Python
    # analogue; apply_overrides uses _jsonpath_set instead.
    modules: ClassVar[dict[str, ModuleSupplier] | None] = None

    def __init__(
        self, definition: dict[str, object] | None = None, submodule: bool | None = None
    ) -> None:
        """Java: Module#Module.

        Java overloads:
        ()
        (JsonObject definition, boolean submodule)
        """
        self.name: str | None = None
        self.specialty: str | None = None
        self.submodule: bool = False
        self.submodule_name: str | None = None
        self.gmf_version: float | None = None
        self.remarks: list[str] | None = None
        self.states: dict[str, State] | None = None
        # Python-only marker: registry key of a hand-written Java core
        # module whose Python class is not ported yet (None otherwise).
        self.core_pending: str | None = None
        if definition is None:
            # Java: protected no-args constructor, used by subclasses,
            # clone() and the core-module shells.
            return
        self.name = f"{definition['name']} Module"
        if "specialty" in definition:
            self.specialty = cast("str | None", definition["specialty"])
        if "gmf_version" in definition:
            self.gmf_version = float(cast(float, definition["gmf_version"]))
            if self.gmf_version > Module.GMF_VERSION:
                raise RuntimeError(
                    f"{self.name} specifies GMF version {self.gmf_version:.6f} in JSON, "
                    f"which is beyond the known GMF version of {Module.GMF_VERSION:.6f}"
                )
        self.submodule = bool(submodule)
        self.remarks = []
        if "remarks" in definition:
            raw_remarks = definition["remarks"]
            if isinstance(raw_remarks, list):
                self.remarks = [str(value) for value in raw_remarks]
        json_states = cast("dict[str, dict[str, object]]", definition["states"])
        self.states = {}
        for state_name, state_definition in json_states.items():
            state = State.build(self, state_name, state_definition)
            self.states[state_name] = state

    @staticmethod
    def _registry() -> dict[str, ModuleSupplier]:
        """The static registry, loaded on first use (Java: the static
        ``modules`` field, initialized when the class is first used)."""
        if Module.modules is None:
            Module.modules = Module.load_modules()
        return Module.modules

    @staticmethod
    def load_modules() -> dict[str, ModuleSupplier]:
        """Java: Module#loadModules.

        Java overloads:
        ()
        """
        ret_val: dict[str, ModuleSupplier] = {}
        submodule_count = 0

        for key, core_name, pending in _CORE_MODULES:
            shell = Module()
            shell.name = core_name
            shell.core_pending = pending
            ret_val[key] = ModuleSupplier(shell)

        module_overrides = Module.get_module_overrides()

        try:
            module_paths = Module.get_module_paths()
            for path in module_paths:
                submodule_count += Module.walk_module_tree(path, ret_val, module_overrides, False)
        except Exception:
            traceback.print_exc()

        print(f"Scanned {len(ret_val) - submodule_count} modules and {submodule_count} submodules.")
        return ret_val

    @staticmethod
    def get_module_paths() -> list[Path]:
        """Java: Module#getModulePaths.

        Java overloads:
        ()
        """
        # Java enumerates every classpath root's "modules" directory; the
        # Python port has the single resources root.
        modules_root = resource_path("modules")
        if modules_root.is_dir():
            return [modules_root]
        return []

    @staticmethod
    def get_module_overrides() -> dict[str, str] | None:
        """Java: Module#getModuleOverrides.

        Java overloads:
        ()
        """
        module_override_file = Config.get("module_override")
        overrides: dict[str, str] | None = None
        if module_override_file is not None and module_override_file.strip() != "":
            try:
                from synthea.helpers.config import _parse_properties

                text = Path(module_override_file).read_bytes().decode("latin-1")
                overrides = _parse_properties(text)
            except OSError:
                traceback.print_exc()
        return overrides

    @staticmethod
    def walk_module_tree(
        modules_path: Path,
        ret_val: dict[str, ModuleSupplier],
        overrides: dict[str, str] | None,
        local_files: bool,
    ) -> int:
        """Java: Module#walkModuleTree.

        Java overloads:
        (Path modulesPath, Map retVal, Properties overrides, boolean localFiles)
        """
        submodule_count = 0
        base_path = modules_path.parent

        def action(t: Path) -> None:
            nonlocal submodule_count
            relative_path = Module.relative_path(t, modules_path)
            submodule = t.parent != modules_path
            if submodule:
                submodule_count += 1
            load_path = t if local_files else Path(t.relative_to(base_path))

            def loader(
                load_path: Path = load_path,
                submodule: bool = submodule,
                overrides: dict[str, str] | None = overrides,
                local_files: bool = local_files,
            ) -> Module:
                return Module.load_file(load_path, submodule, overrides, local_files)

            ret_val[relative_path] = ModuleSupplier(submodule, relative_path, loader)

        Utilities.walk_all_modules(modules_path, action)
        return submodule_count

    @staticmethod
    def add_modules(dir: Path) -> None:
        """Java: Module#addModules.

        Java overloads:
        (File dir)
        """
        registry = Module._registry()
        submodule_count = 0
        original_module_count = len(registry)
        module_overrides = Module.get_module_overrides()
        try:
            submodule_count = Module.walk_module_tree(
                Path(dir).absolute(), registry, module_overrides, True
            )
        except Exception:
            traceback.print_exc()
        print(
            f"Scanned {len(registry) - (original_module_count + submodule_count)} "
            f"local modules and {submodule_count} local submodules."
        )

    @staticmethod
    def relative_path(file_path: Path, modules_folder: Path) -> str:
        """Java: Module#relativePath.

        Java overloads:
        (Path filePath, Path modulesFolder)
        """
        relative = file_path.relative_to(modules_folder).as_posix()
        # Java: .replaceFirst(".json", "") — a regex replace of the first
        # match of <any char>json — then backslashes become slashes.
        return re.sub(r".json", "", relative, count=1).replace("\\", "/")

    @staticmethod
    def load_file(
        path: Path, submodule: bool, overrides: dict[str, str] | None, local_files: bool
    ) -> Module:
        """Java: Module#loadFile.

        Java overloads:
        (Path path, boolean submodule, Properties overrides, boolean localFiles)
        """
        print(f"Loading {'submodule' if submodule else 'module'} {path.as_posix()}")
        if local_files:
            json_string = path.read_bytes().decode("utf-8")
        else:
            json_string = Utilities.read_resource(path.as_posix())
        if overrides is not None:
            json_string = Module.apply_overrides(json_string, overrides, path.name)
        definition = json.loads(json_string)
        return Module(definition, submodule)

    @staticmethod
    def apply_overrides(json_string: str, overrides: dict[str, str], module_file_name: str) -> str:
        """Java: Module#applyOverrides.

        Java overloads:
        (String jsonString, Properties overrides, String moduleFileName)
        """
        data = json.loads(json_string)
        for key, value in overrides.items():
            # use :: for the separator because filenames cannot contain :
            parts = key.split("::")
            module = parts[0]
            if module == module_file_name:
                json_path = parts[1]
                number_value = float(value)  # Java: Double.parseDouble
                _jsonpath_set(data, json_path, number_value)
        return json.dumps(data)

    @staticmethod
    def get_module_names() -> list[str]:
        """Java: Module#getModuleNames.

        Java overloads:
        ()
        """
        return sorted(Module._registry().keys())

    @staticmethod
    def get_modules(
        path_predicate: Callable[[str], bool] | None = None,
    ) -> list[Module]:
        """Java: Module#getModules.

        Java overloads:
        ()
        (Predicate pathPredicate)
        """
        predicate = path_predicate if path_predicate is not None else (lambda p: True)
        registry = Module._registry()
        modules: list[Module] = []
        for key in sorted(registry.keys()):
            supplier = registry[key]
            if supplier.submodule:
                supplier.get()  # ensure submodules get loaded
            elif supplier.core or predicate(supplier.path):
                modules.append(supplier.get())
        return modules

    @staticmethod
    def get_module_suppliers(
        predicate: Callable[[ModuleSupplier], bool] | None = None,
    ) -> list[ModuleSupplier]:
        """Java: Module#getModuleSuppliers.

        Java overloads:
        ()
        (Predicate predicate)
        """
        supplier_predicate = predicate if predicate is not None else (lambda p: True)
        registry = Module._registry()
        return [
            registry[key] for key in sorted(registry.keys()) if supplier_predicate(registry[key])
        ]

    @staticmethod
    def get_module_by_path(path: str) -> Module | None:
        """Java: Module#getModuleByPath.

        Java overloads:
        (String path)
        """
        supplier = Module._registry().get(path)
        return None if supplier is None else supplier.get()

    def clone(self) -> Module:
        """Java: Module#clone.

        Java overloads:
        ()
        """
        clone = Module()
        clone.name = self.name
        clone.specialty = self.specialty
        clone.submodule = self.submodule
        if clone.submodule:
            # Only if this is a submodule, it wants to remember its own
            # name; later, the `name` will be overwritten by the
            # top-level module.
            clone.submodule_name = clone.name
        clone.remarks = self.remarks
        clone.core_pending = self.core_pending
        # Java quirk, reproduced: clone() does not copy gmfVersion.
        if self.states is not None:
            clone.states = {}
            for key in self.states:
                state = self.states[key].clone()
                state.module = clone
                clone.states[key] = state
        return clone

    def process(self, person: Person, time: int, terminate_on_death: bool | None = None) -> bool:
        """Java: Module#process.

        Java overloads:
        (Person person, long time)
        (Person person, long time, boolean terminateOnDeath)
        """
        if self.core_pending is not None:
            raise NotImplementedError(
                f"Java core module {self.name}: {self.core_pending} — "
                "out of scope for T19 (hand-written Java module)"
            )
        if terminate_on_death is None:
            terminate_on_death = True
        if terminate_on_death and not person.alive(time):
            return True
        # Possibly reset wellness encounters for this module.
        from synthea.modules.encounter_module import EncounterModule

        active_key = EncounterModule.ACTIVE_WELLNESS_ENCOUNTER + " " + str(self.name)
        if active_key not in person.attributes:
            # "false" means the person has not entered (or is still
            # within) a wellness encounter
            person.attributes[active_key] = False
        person.history = None
        # what current state is this person in?
        history_key = self.name
        if self.submodule:
            history_key = self.submodule_name
        assert history_key is not None
        if history_key not in person.attributes:
            person.history = []
            initial = self.initial_state()
            person.history.append(initial)
            person.attributes[history_key] = person.history
            # TODO - determining whether or not this the first time a
            # person has entered a submodule is currently not easily
            # computed, so we use `true` below (Java comment).
            _transition_metrics_enter(history_key, str(initial.name), True)
        person.history = person.attributes.get(history_key)  # type: ignore[assignment]
        assert person.history is not None
        current = person.history[0]
        # process the current state, looping until module is finished,
        # probably more than one state
        while current.run(person, time, terminate_on_death):
            entered = current.entered
            exited = current.exited
            assert entered is not None and exited is not None
            duration = exited - entered
            next_state_name = current.transition(person, time)
            first_time = not person.had_prior_state(next_state_name)
            _transition_metrics_exit(history_key, str(current.name), next_state_name, duration)
            assert self.states is not None
            # clone the state so we don't dirty the original
            current = self.states[next_state_name].clone()
            person.history.insert(0, current)
            _transition_metrics_enter(history_key, next_state_name, first_time)
            if exited is not None and exited < time:
                # stop if the patient died in the meantime...
                if terminate_on_death and not person.alive(exited):
                    return True
                # This must be a delay state that expired between cycles,
                # so temporarily rewind time
                if self.process(person, exited, terminate_on_death) and terminate_on_death:
                    # if the patient died during the delay, stop
                    return True
                current = person.history[0]
        return isinstance(current, Terminal)

    def initial_state(self) -> State:
        """Java: Module#initialState.

        Java overloads:
        ()
        """
        assert self.states is not None
        return self.states["Initial"].clone()  # all Initial states are
        # named Initial

    def get_state(self, name: str) -> State | None:
        """Java: Module#getState.

        Java overloads:
        (String name)
        """
        assert self.states is not None
        return self.states.get(name)

    def get_state_names(self) -> set[str]:
        """Java: Module#getStateNames.

        Java overloads:
        ()
        """
        if self.states is None:
            # ex, if this is a non-GMF module
            return set()
        return set(self.states.keys())


class ModuleSupplier:
    """Java: ModuleSupplier — lazy loading of Modules."""

    def __init__(
        self,
        submodule_or_module: bool | Module,
        path: str | None = None,
        loader: Callable[[], Module] | None = None,
    ) -> None:
        """Java: ModuleSupplier#ModuleSupplier.

        Java overloads:
        (boolean submodule, String path, Callable loader)
        (Module module)
        """
        self.core: bool
        self.submodule: bool
        self.path: str
        self.loaded: bool
        self.loader: Callable[[], Module] | None
        self.module: Module | None
        self.fault: BaseException | None
        if isinstance(submodule_or_module, Module):
            module = submodule_or_module
            self.core = True
            self.submodule = module.submodule
            self.path = "core/" + str(module.name)
            self.module = module
            self.loaded = True
            self.loader = None
            self.fault = None
        else:
            if path is None:
                raise TypeError("path is required (Java: Objects.requireNonNull)")
            if loader is None:
                raise TypeError("loader is required (Java: Objects.requireNonNull)")
            self.core = False
            self.submodule = bool(submodule_or_module)
            self.path = path
            self.loaded = False
            self.loader = loader
            self.module = None
            self.fault = None

    def get(self) -> Module:
        """Java: ModuleSupplier#get.

        Java overloads:
        ()
        """
        if not self.loaded:
            try:
                assert self.loader is not None
                self.module = self.loader()
            except BaseException as e:  # Java: catch (Throwable)
                traceback.print_exc()
                self.fault = e
            finally:
                self.loaded = True
                self.loader = None
        if self.fault is not None:
            raise RuntimeError(str(self.fault)) from self.fault
        assert self.module is not None
        return self.module.clone()


setattr(Module, "ModuleSupplier", ModuleSupplier)  # noqa: B010
