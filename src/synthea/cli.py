"""CLI entry point: run_synthea.

Java: App (default package) — argument parsing, config reload and
validation, then ``new Generator(options, exportOptions).run()``.

Out-of-scope options (PORTING_GUIDE §8) raise ``NotImplementedError``
with a clear message instead of being silently ignored: population
snapshots (``-i``/``-u``), snapshot time travel (``-t``), fixed records
(``-f``), keep-patients filters (``-k``) and the flexporter (``-fm``/``-ig``).
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from collections import deque
from datetime import date, timedelta
from pathlib import Path

from synthea.engine.generator import Generator, GeneratorOptions
from synthea.engine.module import Module
from synthea.export.exporter import ExporterRuntimeOptions
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import parse_boolean, parse_int, parse_long
from synthea.resources import resource_path

_USAGE_LINES = [
    "Usage: run_synthea [options] [state [city]]",
    "Options: [-s seed] [-cs clinicianSeed] [-p populationSize]",
    "         [-ps singlePersonSeed]",
    "         [-r referenceDate as YYYYMMDD]",
    "         [-e endDate as YYYYMMDD]",
    "         [-g gender] [-a minAge-maxAge]",
    "         [-o overflowPopulation]",
    "         [-c localConfigFilePath]",
    "         [-d localModulesDirPath]",
    "         [-i initialPopulationSnapshotPath]",
    "         [-u updatedPopulationSnapshotPath]",
    "         [-t updateTimePeriodInDays]",
    "         [-f fixedRecordPath]",
    "         [-k keepMatchingPatientsPath]",
    "         [--config*=value]",
    "          * any setting from src/main/resources/synthea.properties",
    "",
    "Note: When using both -c (config file) and --config*=value (command-line),",
    "the last one specified wins. For example:",
    "  run_synthea --exporter.baseDirectory=./out1/ -c myconfig.properties",
    "    -> the properties file value for exporter.baseDirectory takes effect",
    "  run_synthea -c myconfig.properties --exporter.baseDirectory=./out1/",
    "    -> the command-line value ./out1/ takes effect",
    "",
    "Examples:",
    "run_synthea Massachusetts",
    "run_synthea Alaska Juneau",
    "run_synthea -s 12345",
    "run_synthea -p 1000",
    "run_synthea -s 987 Washington Seattle",
    'run_synthea -s 21 -p 100 Utah "Salt Lake City"',
    "run_synthea -g M -a 60-65",
    "run_synthea -p 10 --exporter.fhir.export=true",
    'run_synthea --exporter.baseDirectory="./output_tx/" Texas',
]


def _parse_yyyymmdd(value: str | None) -> int:
    """Java: ``new SimpleDateFormat("yyyyMMdd")`` (UTC, lenient) ``.parse(value).getTime()``.

    Lenient in the Java sense: out-of-range months and days roll over
    into neighbouring months/years instead of failing.
    """
    if value is None:
        raise TypeError("SimpleDateFormat.parse(null): NullPointerException")
    text = value.strip()
    if len(text) < 8 or not text[:8].isdigit():
        raise ValueError(f"Unparseable date: {value!r}")
    year, month, day = int(text[0:4]), int(text[4:6]), int(text[6:8])
    total_months = year * 12 + (month - 1)
    rolled_year, rolled_month0 = divmod(total_months, 12)
    first = date(rolled_year, rolled_month0 + 1, 1) + timedelta(days=day - 1)
    epoch_days = (first - date(1970, 1, 1)).days
    return epoch_days * 86_400_000


def _required(value: str | None) -> str:
    """Java: passing a missing (null) argument value into a parse throws."""
    if value is None:
        raise TypeError("argument value missing (Java: NullPointerException)")
    return value


class App:
    """Java: App (default package)."""

    def __init__(self) -> None:
        """Java: App#App.

        Java overloads:
        ()
        """
        # Java: the implicit public constructor of a utility class; never used.

    @staticmethod
    def usage() -> None:
        """Java: App#usage.

        Java overloads:
        ()
        """
        for line in _USAGE_LINES:
            print(line)

    @staticmethod
    def main(args: list[str]) -> None:
        """Java: App#main.

        Java overloads:
        (String args)
        """
        # CSV-only port default: Java loads custom exporters from the
        # classpath via ServiceLoader; there is no classpath here and the
        # Exporter raises if this default-on flag is left true (its warning
        # text: "The CLI defaults it to false"). An explicit
        # --exporter.enable_custom_exporters=true or -c file value set
        # during the scan below overrides this and raises there instead.
        Config.set("exporter.enable_custom_exporters", "false")

        options = GeneratorOptions()
        export_options = ExporterRuntimeOptions()

        valid_args = True
        override_future_date_error = False
        reload_config = False
        if args:
            try:
                args_q: deque[str] = deque(args)
                while args_q:
                    curr_arg = args_q.popleft()
                    lowered = curr_arg.lower()
                    if lowered in ("-h", "--help"):
                        App.usage()
                        return
                    elif lowered == "-s":
                        options.seed = parse_long(_required(args_q.popleft() if args_q else None))
                    elif lowered == "-cs":
                        options.clinician_seed = parse_long(
                            _required(args_q.popleft() if args_q else None)
                        )
                    elif lowered == "-ps":
                        options.single_person_seed = parse_long(
                            _required(args_q.popleft() if args_q else None)
                        )
                    elif lowered == "-r":
                        options.reference_time = _parse_yyyymmdd(
                            args_q.popleft() if args_q else None
                        )
                    elif lowered == "-e":
                        if curr_arg == "-E":
                            override_future_date_error = True
                        options.end_time = _parse_yyyymmdd(args_q.popleft() if args_q else None)
                    elif lowered == "-p":
                        value = _required(args_q.popleft() if args_q else None)
                        options.population = parse_int(value)
                        Config.set("generate.default_population", value)
                    elif lowered == "-o":
                        options.overflow = parse_boolean(
                            _required(args_q.popleft() if args_q else None)
                        )
                    elif lowered == "-g":
                        value = _required(args_q.popleft() if args_q else None)
                        if value in ("M", "F"):
                            options.gender = value
                        else:
                            raise ValueError("Legal values for gender are 'M' or 'F'.")
                    elif lowered == "-a":
                        value = _required(args_q.popleft() if args_q else None)
                        if "-" in value:
                            values = value.split("-")
                            options.age_specified = True
                            options.min_age = parse_int(values[0])
                            options.max_age = parse_int(values[1])
                        else:
                            raise ValueError("Age format: minAge-maxAge. E.g. 60-65.")
                    elif lowered == "-m":
                        value = _required(args_q.popleft() if args_q else None)
                        options.enabled_modules = value.split(os.pathsep)
                    elif lowered == "-c":
                        value = _required(args_q.popleft() if args_q else None)
                        Config.load(Path(value))
                        reload_config = True
                    elif lowered == "-d":
                        value = _required(args_q.popleft() if args_q else None)
                        local_module_dir = Path(value)
                        if local_module_dir.exists() and local_module_dir.is_dir():
                            Module.add_modules(local_module_dir)
                        else:
                            raise FileNotFoundError(
                                "Specified local module directory "
                                f"({local_module_dir.absolute()}) is not a directory"
                            )
                    elif lowered == "-u":
                        _required(args_q.popleft() if args_q else None)
                        App.fail_if_physiology_enabled(curr_arg)
                        raise NotImplementedError(
                            "-u (updated population snapshot) is out of scope: "
                            "population snapshots are not ported yet"
                        )
                    elif lowered == "-i":
                        value = _required(args_q.popleft() if args_q else None)
                        App.fail_if_physiology_enabled(curr_arg)
                        file = Path(value)
                        if not (file.exists() and os.access(file, os.R_OK)):
                            raise OSError(
                                f"Unable to load snapshot file ({file.absolute()}): "
                                "File does not exist or is not readable"
                            )
                        raise NotImplementedError(
                            "-i (initial population snapshot) is out of scope: "
                            "population snapshots are not ported yet"
                        )
                    elif curr_arg.startswith("-t"):
                        _required(args_q.popleft() if args_q else None)
                        raise NotImplementedError(
                            "-t (updateTimePeriodInDays) is out of scope: it applies "
                            "to population snapshots, which are not ported yet"
                        )
                    elif lowered == "-f":
                        value = _required(args_q.popleft() if args_q else None)
                        fixed_record_path = Path(value)
                        if not fixed_record_path.exists():
                            raise FileNotFoundError(
                                f"Specified fixed record file ({value}) does not exist"
                            )
                        raise NotImplementedError(
                            "-f (fixed records) is out of scope: fixed records / "
                            "identity are not ported yet"
                        )
                    elif curr_arg == "-k":
                        value = _required(args_q.popleft() if args_q else None)
                        keep_file = Path(value)
                        if (
                            not keep_file.exists()
                            and not (resource_path("keep_modules") / value).exists()
                        ):
                            raise FileNotFoundError(
                                f"Specified keep-patients file ({value}) does not exist"
                            )
                        raise NotImplementedError(
                            "-k (keep-patients) is out of scope: keep-patients "
                            "filters are not ported yet"
                        )
                    elif curr_arg == "-fm":
                        _required(args_q.popleft() if args_q else None)
                        raise NotImplementedError(
                            "-fm (flexporter mapping) is out of scope: the "
                            "flexporter is not ported yet"
                        )
                    elif curr_arg == "-ig":
                        _required(args_q.popleft() if args_q else None)
                        raise NotImplementedError(
                            "-ig (flexporter IG) is out of scope: the flexporter is not ported yet"
                        )
                    elif curr_arg.startswith("--"):
                        if "=" in curr_arg:
                            config_setting, _, value = curr_arg[2:].partition("=")
                        else:
                            config_setting = curr_arg[2:]
                            value = _required(args_q.popleft() if args_q else None)
                        Config.set(config_setting, value)
                        reload_config = True
                    elif options.state is None:
                        options.state = curr_arg
                    else:
                        # assume it must be the city
                        options.city = curr_arg
            except NotImplementedError:
                raise
            except Exception:
                traceback.print_exc()
                App.usage()
                valid_args = False

        if reload_config:
            App.reset_options_from_config(options, export_options)

        if valid_args and App.validate_config(options, override_future_date_error):
            generator = Generator(options, export_options)
            generator.run()

    @staticmethod
    def reset_options_from_config(
        options: GeneratorOptions, export_options: ExporterRuntimeOptions
    ) -> None:
        """Java: App#resetOptionsFromConfig.

        Java overloads:
        (Generator.GeneratorOptions options, Exporter.ExporterRuntimeOptions
        exportOptions)
        """
        # Any options that are automatically set by reading the configuration
        # file during options initialization need to be reset here.
        options.population = Config.get_as_integer("generate.default_population", 1)
        options.thread_pool_size = Config.get_as_integer("generate.thread_pool_size", -1)

        export_options.years_of_history = Config.get_as_integer("exporter.years_of_history", 10)
        export_options.terminology_service = (
            Config.get("generate.terminology_service_url", "") or ""
        ) != ""

    @staticmethod
    def validate_config(options: GeneratorOptions, override_future_date_error: bool) -> bool:
        """Java: App#validateConfig.

        Java overloads:
        (Generator.GeneratorOptions options, boolean overrideFutureDateError)
        """
        valid = True
        if (
            Config.get_as_boolean("exporter.fhir.transaction_bundle")
            and not Config.get_as_boolean("exporter.practitioner.fhir.export")
            and not Config.get_as_boolean("exporter.hospital.fhir.export")
        ):
            print(
                "Warning: Synthea is configured to export FHIR transaction bundles "
                "for generated patients but not to export the practitioners and organizations "
                "that the patient bundle entries will reference. "
                "See https://github.com/synthetichealth/synthea/wiki/FHIR-Transaction-Bundles "
                "for more information."
            )
        if not override_future_date_error:
            years_of_history = Config.get_as_integer("exporter.years_of_history")
            millis_to_end_time = options.end_time - int(time.time() * 1000)
            if millis_to_end_time > Utilities.convert_time("years", years_of_history):
                print(
                    "Error: the specified end time is further in the future than the "
                    "number of years of export history. The first exported events will be in the "
                    "future. Consider adjusting the values of the '-e endDate' command line switch "
                    "and the 'exporter.years_of_history' configuration file entry.\n"
                    "You may override this error by using '-E endDate' instead of '-e EndDate'."
                )
                valid = False
        return valid

    @staticmethod
    def fail_if_physiology_enabled(arg: str) -> None:
        """Java: App#failIfPhysiologyEnabled.

        Java overloads:
        (String arg)
        """
        if parse_boolean(Config.get("physiology.generators.enabled", "false") or "false"):
            raise ValueError(
                f"The {arg} command line switch cannot be used when physiology "
                "generators are enabled - set configuration option "
                "physiology.generators.enabled=false to use"
            )


def main(argv: list[str] | None = None) -> int:
    """Java: App#main(String[]); run_synthea entry point."""
    App.main(list(sys.argv[1:] if argv is None else argv))
    return 0
