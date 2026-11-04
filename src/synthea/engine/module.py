"""Java API skeleton: Module.java."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.state import State
    from synthea.world.agents.person import Person

    class Configuration(Protocol):
        """Java boundary type: Configuration; external to the mapped Python port."""

    class Throwable(Protocol):
        """Java boundary type: Throwable; external to the mapped Python port."""


class Module:
    """Java: Module; pending T19."""

    GMF_VERSION: ClassVar[float] = 2.0
    JSON_PATH_CONFIG: ClassVar[Configuration]  # Java initialization deferred to T19.
    modules: ClassVar[dict[str, ModuleSupplier]]  # Java initialization deferred to T19.

    def __init__(
        self, definition: dict[str, object] | None = None, submodule: bool | None = None
    ) -> None:
        """Java: Module#Module.

        Java overloads:
        ()
        (JsonObject definition, boolean submodule)
        """
        self.name: str
        self.specialty: str
        self.submodule: bool
        self.submodule_name: str
        self.gmf_version: float
        self.remarks: list[str]
        self.states: dict[str, State]
        raise NotImplementedError("Java: Module#Module — pending T19")

    @staticmethod
    def load_modules() -> dict[str, ModuleSupplier]:
        """Java: Module#loadModules.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#loadModules — pending T19")

    @staticmethod
    def get_module_paths() -> list[Path]:
        """Java: Module#getModulePaths.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#getModulePaths — pending T19")

    @staticmethod
    def get_module_overrides() -> dict[str, str]:
        """Java: Module#getModuleOverrides.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#getModuleOverrides — pending T19")

    @staticmethod
    def walk_module_tree(
        modules_path: Path,
        ret_val: dict[str, ModuleSupplier],
        overrides: dict[str, str],
        local_files: bool,
    ) -> int:
        """Java: Module#walkModuleTree.

        Java overloads:
        (Path modulesPath, Map retVal, Properties overrides, boolean localFiles)
        """
        raise NotImplementedError("Java: Module#walkModuleTree — pending T19")

    @staticmethod
    def add_modules(dir: Path) -> None:
        """Java: Module#addModules.

        Java overloads:
        (File dir)
        """
        raise NotImplementedError("Java: Module#addModules — pending T19")

    @staticmethod
    def relative_path(file_path: Path, modules_folder: Path) -> str:
        """Java: Module#relativePath.

        Java overloads:
        (Path filePath, Path modulesFolder)
        """
        raise NotImplementedError("Java: Module#relativePath — pending T19")

    @staticmethod
    def load_file(
        path: Path, submodule: bool, overrides: dict[str, str], local_files: bool
    ) -> Module:
        """Java: Module#loadFile.

        Java overloads:
        (Path path, boolean submodule, Properties overrides, boolean localFiles)
        """
        raise NotImplementedError("Java: Module#loadFile — pending T19")

    @staticmethod
    def apply_overrides(json_string: str, overrides: dict[str, str], module_file_name: str) -> str:
        """Java: Module#applyOverrides.

        Java overloads:
        (String jsonString, Properties overrides, String moduleFileName)
        """
        raise NotImplementedError("Java: Module#applyOverrides — pending T19")

    @staticmethod
    def get_module_names() -> list[str]:
        """Java: Module#getModuleNames.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#getModuleNames — pending T19")

    @staticmethod
    def get_modules(path_predicate: Callable[[str], bool] | None = None) -> list[Module]:
        """Java: Module#getModules.

        Java overloads:
        ()
        (Predicate pathPredicate)
        """
        raise NotImplementedError("Java: Module#getModules — pending T19")

    @staticmethod
    def get_module_suppliers(
        predicate: Callable[[ModuleSupplier], bool] | None = None,
    ) -> list[ModuleSupplier]:
        """Java: Module#getModuleSuppliers.

        Java overloads:
        ()
        (Predicate predicate)
        """
        raise NotImplementedError("Java: Module#getModuleSuppliers — pending T19")

    @staticmethod
    def get_module_by_path(path: str) -> Module:
        """Java: Module#getModuleByPath.

        Java overloads:
        (String path)
        """
        raise NotImplementedError("Java: Module#getModuleByPath — pending T19")

    def clone(self) -> Module:
        """Java: Module#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#clone — pending T19")

    def process(self, person: Person, time: int, terminate_on_death: bool | None = None) -> bool:
        """Java: Module#process.

        Java overloads:
        (Person person, long time)
        (Person person, long time, boolean terminateOnDeath)
        """
        raise NotImplementedError("Java: Module#process — pending T19")

    def initial_state(self) -> State:
        """Java: Module#initialState.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#initialState — pending T19")

    def get_state(self, name: str) -> State:
        """Java: Module#getState.

        Java overloads:
        (String name)
        """
        raise NotImplementedError("Java: Module#getState — pending T19")

    def get_state_names(self) -> list[str]:
        """Java: Module#getStateNames.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Module#getStateNames — pending T19")


class ModuleSupplier:
    """Java: ModuleSupplier; pending T19."""

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
        self.loader: Callable[[], Module]
        self.module: Module
        self.fault: Throwable
        raise NotImplementedError("Java: ModuleSupplier#ModuleSupplier — pending T19")

    def get(self) -> Module:
        """Java: ModuleSupplier#get.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ModuleSupplier#get — pending T19")


setattr(Module, "ModuleSupplier", ModuleSupplier)  # noqa: B010
