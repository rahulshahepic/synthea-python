"""Java API skeleton: App.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.engine.generator import GeneratorOptions as GeneratorGeneratorOptions
    from synthea.export.exporter import ExporterRuntimeOptions as ExporterExporterRuntimeOptions


class App:
    """Java: .App; pending T28."""

    def __init__(self) -> None:
        """Java: App#App.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: App#App — pending T28")

    @staticmethod
    def usage() -> None:
        """Java: App#usage.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: App#usage — pending T28")

    @staticmethod
    def main(args: list[str]) -> None:
        """Java: App#main.

        Java overloads:
        (String args)
        """
        raise NotImplementedError("Java: App#main — pending T28")

    @staticmethod
    def reset_options_from_config(
        options: GeneratorGeneratorOptions, export_options: ExporterExporterRuntimeOptions
    ) -> None:
        """Java: App#resetOptionsFromConfig.

        Java overloads:
        (Generator.GeneratorOptions options, Exporter.ExporterRuntimeOptions
        exportOptions)
        """
        raise NotImplementedError("Java: App#resetOptionsFromConfig — pending T28")

    @staticmethod
    def validate_config(
        options: GeneratorGeneratorOptions, override_future_date_error: bool
    ) -> bool:
        """Java: App#validateConfig.

        Java overloads:
        (Generator.GeneratorOptions options, boolean overrideFutureDateError)
        """
        raise NotImplementedError("Java: App#validateConfig — pending T28")

    @staticmethod
    def fail_if_physiology_enabled(arg: str) -> None:
        """Java: App#failIfPhysiologyEnabled.

        Java overloads:
        (String arg)
        """
        raise NotImplementedError("Java: App#failIfPhysiologyEnabled — pending T28")


def main(argv: list[str] | None = None) -> int:
    """Java: App#main(String[]); run_synthea entry point, pending T28."""
    raise NotImplementedError("Java: App#main — pending T28")
