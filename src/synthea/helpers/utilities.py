"""Utilities port.

Java: org.mitre.synthea.helpers.Utilities — time conversions, comparisons,
resource reading and assorted helpers.

Calendar methods use ``java.util.GregorianCalendar`` (the default calendar
for the en-US parity JVM): a hybrid Julian/Gregorian calendar whose cutover
day is Gregorian 1582-10-15 (the day after Julian 1582-10-04). The
``LocalDate`` methods are proleptic Gregorian (ISO), exactly like
``java.time``. ``Calendar.YEAR`` has no year zero: astronomical year 0 is
1 BC and ``get(Calendar.YEAR)`` returns 1 with era BC, astronomical -5
returns 6 BC, and so on; ``convertCalendarYearsToTime`` sets the YEAR field
with era AD, which the JDK resolves to the astronomical year of the same
number (verified against JDK 21 for years -2000..3000 by the probe).
"""

from __future__ import annotations

import math
import re
import struct
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, NamedTuple, Protocol, cast

from synthea.helpers.config import Config
from synthea.javacompat.hashing import string_compare_to
from synthea.javacompat.numbers import (
    d2i,
    d2l,
    parse_boolean,
    parse_double,
    parse_int,
    parse_long,
)
from synthea.resources import resource_path

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.concepts.health_record import Code


class Gson(Protocol):
    """Java boundary type: Gson; external to the mapped Python port."""


class JsonPrimitive(Protocol):
    """Java boundary type: JsonPrimitive; external to the mapped Python port."""


class URI(Protocol):
    """Java boundary type: URI; external to the mapped Python port."""

    @property
    def scheme(self) -> str | None:
        """The URI scheme (Java: URI#getScheme)."""
        ...


class BiConsumer(Protocol):
    """Java boundary type: BiConsumer; external to the mapped Python port."""

    def __call__(self, a: Path, b: Path) -> None:
        """Java: BiConsumer#accept."""
        ...


_LONG_MAX = 9223372036854775807
_LONG_MIN = -9223372036854775808

# ---------------------------------------------------------------------------
# Hybrid Julian/Gregorian calendar arithmetic (java.util.GregorianCalendar).
# Day counts are days since 1970-01-01 (a Gregorian date). Conversions use
# Howard Hinnant's civil algorithms with floor division, which Python's //
# provides directly; the Julian variants use the 4-year leap cycle and were
# calibrated against JDK 21 (see docs/porting_notes/T06.md).
# ---------------------------------------------------------------------------

_CUTOVER_DAYS: int | None = None


def _gregorian_days_from_civil(y: int, m: int, d: int) -> int:
    """Proleptic Gregorian (y, m, d) -> days since 1970-01-01."""
    y -= 1 if m <= 2 else 0
    era = y // 400
    yoe = y - era * 400
    mp = m - 3 if m > 2 else m + 9
    doy = (153 * mp + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _gregorian_civil_from_days(z: int) -> tuple[int, int, int]:
    """Days since 1970-01-01 -> proleptic Gregorian (y, m, d)."""
    z += 719468
    era = z // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    return (y + (1 if m <= 2 else 0), m, d)


def _julian_days_from_civil(y: int, m: int, d: int) -> int:
    """Julian-calendar (y, m, d) -> days since 1970-01-01."""
    y -= 1 if m <= 2 else 0
    era = y // 4
    yoe = y - era * 4
    mp = m - 3 if m > 2 else m + 9
    doy = (153 * mp + 2) // 5 + d - 1
    return era * 1461 + yoe * 365 + doy - 719470


def _julian_civil_from_days(z: int) -> tuple[int, int, int]:
    """Days since 1970-01-01 -> Julian-calendar (y, m, d)."""
    z += 719470
    era = z // 1461
    doe = z - era * 1461
    yoe = 3 if doe == 1460 else doe // 365
    doy = doe - yoe * 365
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    y = era * 4 + yoe + (1 if m <= 2 else 0)
    return (y, m, d)


def _cutover_days() -> int:
    """Days since epoch of Gregorian 1582-10-15, the first Gregorian day."""
    global _CUTOVER_DAYS
    if _CUTOVER_DAYS is None:
        _CUTOVER_DAYS = _gregorian_days_from_civil(1582, 10, 15)
    return _CUTOVER_DAYS


def _hybrid_days_from_civil(y: int, m: int, d: int) -> int:
    """GregorianCalendar (y, m, d) -> days since 1970-01-01.

    Mirrors GregorianCalendar: dates on/after the cutover are Gregorian,
    earlier dates are Julian.
    """
    greg = _gregorian_days_from_civil(y, m, d)
    if greg >= _cutover_days():
        return greg
    return _julian_days_from_civil(y, m, d)


def _hybrid_civil_from_days(z: int) -> tuple[int, int, int]:
    """Days since 1970-01-01 -> GregorianCalendar (y, m, d), astronomical year."""
    if z >= _cutover_days():
        return _gregorian_civil_from_days(z)
    return _julian_civil_from_days(z)


def _calendar_year_field(astronomical_year: int) -> int:
    """Java: Calendar.YEAR for a date (era is not returned by Utilities)."""
    return astronomical_year if astronomical_year >= 1 else 1 - astronomical_year


def _timeunit_to_millis(value: int, unit_millis: int) -> int:
    """Java: java.util.concurrent.TimeUnit#toMillis — saturating multiply."""
    result = value * unit_millis
    if result > _LONG_MAX:
        return _LONG_MAX
    if result < _LONG_MIN:
        return _LONG_MIN
    return result


_DATE_RANGE_RE = re.compile(r"^(\d{4}\-\d{2}\-\d{2})\-(\d{4}\-\d{2}\-\d{2})$")


class LongRange(NamedTuple):
    """Java: org.apache.commons.lang3.Range<Long> from parseDateRange.

    An external library value type (not Components.Range); only the
    minimum/maximum pair is observable by Synthea callers.
    """

    minimum: int
    maximum: int


def _parse_local_date(text: str) -> date:
    """Java: LocalDate.parse(text, DateTimeFormatter.ISO_LOCAL_DATE).

    Raises ValueError where Java throws DateTimeParseException.
    """
    parts = text.split("-")
    try:
        if len(parts) != 3:
            raise ValueError(text)
        year, month, day = (int(p) for p in parts)
        return date(year, month, day)
    except ValueError:
        raise ValueError(f"Text '{text}' could not be parsed") from None


def _local_date_to_epoch_milli(d: date) -> int:
    """LocalDate.atStartOfDay().toInstant(UTC).toEpochMilli() (proleptic)."""
    return _gregorian_days_from_civil(d.year, d.month, d.day) * 86400000


class Utilities:
    """Java: org.mitre.synthea.helpers.Utilities."""

    SYNTHEA_VERSION: ClassVar[str]  # Set by the static initializer below.

    def __init__(self) -> None:
        """Java: Utilities#Utilities.

        Java overloads:
        ()
        """

    @staticmethod
    def convert_time(units: str, value: int | float) -> int:
        """Java: Utilities#convertTime.

        Java overloads:
        (String units, long value)
        (String units, double value)

        A Python int dispatches to the long overload and a float to the
        double overload, mirroring Java overload resolution at call sites
        (int literals widen to long in preference to double).
        """
        if isinstance(value, float):
            return Utilities._convert_time_double(units, value)
        return Utilities._convert_time_long(units, value)

    @staticmethod
    def _convert_time_long(units: str, value: int) -> int:
        """Java: Utilities#convertTime(String, long)."""
        match units:
            case "hours":
                return _timeunit_to_millis(value, 3600000)
            case "minutes":
                return _timeunit_to_millis(value, 60000)
            case "seconds":
                return _timeunit_to_millis(value, 1000)
            case "days":
                return _timeunit_to_millis(value, 86400000)
            case "years":
                # (long) 365.25 * value == 365 * value, a wrapping long
                # multiply, then a saturating DAYS.toMillis.
                wrapped = ((365 * value + 2**63) % 2**64) - 2**63
                return _timeunit_to_millis(wrapped, 86400000)
            case "months":
                # 30 * value is a wrapping long multiply in Java, then a
                # saturating DAYS.toMillis.
                wrapped = ((30 * value + 2**63) % 2**64) - 2**63
                return _timeunit_to_millis(wrapped, 86400000)
            case "weeks":
                # 7 * value is a wrapping long multiply in Java, then a
                # saturating DAYS.toMillis.
                wrapped = ((7 * value + 2**63) % 2**64) - 2**63
                return _timeunit_to_millis(wrapped, 86400000)
            case _:
                raise RuntimeError(f"Unexpected time unit: {units}")

    @staticmethod
    def _convert_time_double(units: str, value: float) -> int:
        """Java: Utilities#convertTime(String, double)."""
        match units:
            case "hours":
                return _timeunit_to_millis(d2l(60.0 * value), 60000)
            case "minutes":
                return _timeunit_to_millis(d2l(60.0 * value), 1000)
            case "seconds":
                return d2l(1000.0 * value)
            case "days":
                return _timeunit_to_millis(d2l(24.0 * value), 3600000)
            case "years":
                return _timeunit_to_millis(d2l(365.25 * value), 86400000)
            case "months":
                return _timeunit_to_millis(d2l(30.0 * value), 86400000)
            case "weeks":
                return _timeunit_to_millis(d2l(7.0 * value), 86400000)
            case _:
                raise RuntimeError(f"Unexpected time unit: {units}")

    @staticmethod
    def convert_calendar_years_to_time(years: int) -> int:
        """Java: Utilities#convertCalendarYearsToTime.

        Java overloads:
        (int years)

        GregorianCalendar cleared, GMT, set(years, Jan 1, 00:00:00.000);
        the YEAR field with era AD resolves to astronomical year ``years``.
        """
        return _hybrid_days_from_civil(years, 1, 1) * 86400000

    @staticmethod
    def get_year(time: int) -> int:
        """Java: Utilities#getYear — the Calendar.YEAR field (no era).

        Java overloads:
        (long time)
        """
        days = time // 86400000
        year, _, _ = _hybrid_civil_from_days(days)
        return _calendar_year_field(year)

    @staticmethod
    def get_month(time: int) -> int:
        """Java: Utilities#getMonth — Calendar.MONTH + 1.

        Java overloads:
        (long time)
        """
        days = time // 86400000
        _, month, _ = _hybrid_civil_from_days(days)
        return month

    @staticmethod
    def local_date_to_timestamp(date_value: date) -> int:
        """Java: Utilities#localDateToTimestamp.

        Java overloads:
        (LocalDate date)
        """
        return _local_date_to_epoch_milli(date_value)

    @staticmethod
    def timestamp_to_local_date(timestamp: int) -> date:
        """Java: Utilities#timestampToLocalDate.

        Java overloads:
        (long timestamp)
        """
        days = timestamp // 86400000
        year, month, day = _gregorian_civil_from_days(days)
        return date(year, month, day)

    @staticmethod
    def get_anniversary(date_value: int, anniversary: int) -> int:
        """Java: Utilities#getAnniversary.

        Java overloads:
        (long date, int anniversary)

        Calendar.set(YEAR, get(YEAR) + anniversary) on the hybrid calendar;
        the era is preserved, so an anniversary on a BC date moves the YEAR
        field within BC (backwards astronomically). Resolution is lenient:
        Feb 29 + 1 year lands on Mar 1.
        """
        days = date_value // 86400000
        millis_of_day = date_value - days * 86400000
        astro_year, month, day = _hybrid_civil_from_days(days)
        if astro_year >= 1:
            new_astro_year = _calendar_year_field(astro_year) + anniversary
        else:
            new_field = _calendar_year_field(astro_year) + anniversary
            new_astro_year = 1 - new_field
        base = _hybrid_days_from_civil(new_astro_year, month, 1)
        return (base + (day - 1)) * 86400000 + millis_of_day

    @staticmethod
    def primitive(p: object) -> object:
        """Java: Utilities#primitive.

        Java overloads:
        (JsonPrimitive p)

        The Python analogue of a Gson JsonPrimitive is the plain value it
        wraps: bool -> Boolean, int/float -> Number, str -> String.
        Numbers go through getAsDouble(); integral doubles come back as
        an int via the Java ``(int)`` cast (truncate, saturate). A None
        argument is a null JsonPrimitive reference, which Java dereferences
        immediately — mirrored here as TypeError (NullPointerException).
        """
        if p is None:
            raise TypeError("JsonPrimitive is null: NullPointerException")
        if isinstance(p, bool):
            return p
        if isinstance(p, int | float):
            double_val = float(p)
            # Java: doubleVal == Math.rint(doubleVal) — true exactly for
            # integral values and for +-Infinity (rint(inf) == inf); NaN
            # compares false and falls through as a Double.
            if double_val.is_integer() or math.isinf(double_val):
                return d2i(double_val)
            return double_val
        if isinstance(p, str):
            return p
        raise TypeError(f"not a JsonPrimitive value: {type(p).__name__}")

    @staticmethod
    def convert_risk_to_timestep(
        risk: float, original_period_in_ms: float, new_time_step_in_ms: float | None = None
    ) -> float:
        """Java: Utilities#convertRiskToTimestep.

        Java overloads:
        (double risk, double originalPeriodInMS) — reads the timestep from
            Config key "generate.timestep".
        (double risk, double originalPeriodInMS, double newTimeStepInMS)
        """
        if new_time_step_in_ms is None:
            new_time_step_in_ms = Config.get_as_double("generate.timestep")
        return 1 - _java_pow(1 - risk, new_time_step_in_ms / original_period_in_ms)

    @staticmethod
    def compare(
        lhs: object | float | bool | str | int | Code,
        rhs: object | float | bool | str | int | Code,
        operator: str,
    ) -> bool:
        """Java: Utilities#compare (all overloads).

        Java overloads:
        (Object lhs, Object rhs, String operator)
        (Double lhs, Double rhs, String operator)
        (Boolean lhs, Boolean rhs, String operator)
        (String lhs, String rhs, String operator)
        (Integer lhs, Integer rhs, String operator)
        (Code lhs, Code rhs, String operator)

        Python dispatch mirrors the Object overload: nil checks first,
        then Number/Boolean/String/Code in Java's instanceof order (bool is
        tested before numbers, since Python bool is an int subclass but a
        Java Boolean is not a Number). Numbers compare as doubles exactly
        as the Object and Double overloads do, except that two ints compare
        exactly, matching the Integer overload (identical results for every
        value a double represents exactly).
        """
        if operator == "is nil":
            return lhs is None
        if operator == "is not nil":
            return lhs is not None
        if lhs is None:
            return False
        if isinstance(lhs, bool) and isinstance(rhs, bool):
            return Utilities._compare_booleans(lhs, rhs, operator)
        if (
            isinstance(lhs, int | float)
            and not isinstance(lhs, bool)
            and isinstance(rhs, int | float)
            and not isinstance(rhs, bool)
        ):
            if isinstance(lhs, int) and isinstance(rhs, int):
                return Utilities._compare_ints(lhs, rhs, operator)
            return Utilities._compare_doubles(float(lhs), float(rhs), operator)
        if isinstance(lhs, str) and isinstance(rhs, str):
            return Utilities._compare_strings(lhs, rhs, operator)
        if (
            hasattr(lhs, "system")
            and hasattr(lhs, "code")
            and hasattr(rhs, "system")
            and hasattr(rhs, "code")
        ):
            return Utilities._compare_codes(lhs, rhs, operator)
        if rhs is None:
            # Java's Object overload builds its "Cannot compare" message with
            # rhs.getClass(), so a null rhs throws NullPointerException
            # instead of the RuntimeException a type mismatch gets.
            raise TypeError("Cannot compare: rhs.getClass() on a null rhs")
        raise RuntimeError(f"Cannot compare {_java_class_name(lhs)} to {_java_class_name(rhs)}.\n")

    @staticmethod
    def _compare_doubles(lhs: float, rhs: float, operator: str) -> bool:
        """Java: Utilities#compare(Double, Double, String)."""
        match operator:
            case "<":
                return lhs < rhs
            case "<=":
                return lhs <= rhs
            case "==":
                return lhs == rhs
            case ">=":
                return lhs >= rhs
            case ">":
                return lhs > rhs
            case "!=":
                return lhs != rhs
            case "is nil":
                return False  # lhs is not None here (checked by caller path)
            case "is not nil":
                return True
            case _:
                print(f"Unsupported operator: {operator}", file=sys.stderr)
                return False

    @staticmethod
    def _compare_booleans(lhs: bool, rhs: bool, operator: str) -> bool:
        """Java: Utilities#compare(Boolean, Boolean, String).

        Java quirk, reproduced: every ordering operator and != returns
        ``lhs != rhs``; only == compares for equality.
        """
        match operator:
            case "<" | "<=" | ">" | ">=" | "!=":
                return lhs != rhs
            case "==":
                return lhs == rhs
            case "is nil":
                return False
            case "is not nil":
                return True
            case _:
                print(f"Unsupported operator: {operator}", file=sys.stderr)
                return False

    @staticmethod
    def _compare_strings(lhs: str, rhs: str, operator: str) -> bool:
        """Java: Utilities#compare(String, String, String)."""
        cmp = string_compare_to(lhs, rhs)
        match operator:
            case "<":
                return cmp < 0
            case "<=":
                return cmp <= 0
            case "==":
                return lhs == rhs
            case ">=":
                return cmp >= 0
            case ">":
                return cmp > 0
            case "!=":
                return lhs != rhs
            case "is nil":
                return False
            case "is not nil":
                return True
            case _:
                print(f"Unsupported operator: {operator}", file=sys.stderr)
                return False

    @staticmethod
    def _compare_ints(lhs: int, rhs: int, operator: str) -> bool:
        """Java: Utilities#compare(Integer, Integer, String)."""
        match operator:
            case "<":
                return lhs < rhs
            case "<=":
                return lhs <= rhs
            case "==":
                return lhs == rhs
            case ">=":
                return lhs >= rhs
            case ">":
                return lhs > rhs
            case "!=":
                return lhs != rhs
            case "is nil":
                return False
            case "is not nil":
                return True
            case _:
                print(f"Unsupported operator: {operator}", file=sys.stderr)
                return False

    @staticmethod
    def _compare_codes(lhs: object, rhs: object, operator: str) -> bool:
        """Java: Utilities#compare(Code, Code, String).

        Only == and != are supported; equality is HealthRecord.Code#equals,
        which compares system and code only (not display). The Code port is
        a T08 stub whose equals() is not yet implemented, so the comparison
        is inlined here from the Java source.
        """
        lhs_code = cast("Code", lhs)
        rhs_code = cast("Code", rhs)
        equal = lhs_code.system == rhs_code.system and lhs_code.code == rhs_code.code
        match operator:
            case "==":
                return equal
            case "!=":
                return not equal
            case "is nil":
                return False
            case "is not nil":
                return True
            case _:
                print(f"Unsupported operator: {operator}", file=sys.stderr)
                return False

    @staticmethod
    def get_synthea_version() -> str:
        """Java: Utilities#getSyntheaVersion.

        Java overloads:
        ()

        Reads the build-generated version.txt resource; any failure or an
        empty file leaves the default "synthea-java".
        """
        version = "synthea-java"
        try:
            text = Utilities.read_resource("version.txt")
            if text is not None and len(text) > 0:
                version = text
        except Exception:
            # Java catches the exception inside getSyntheaVersion, prints
            # the stack trace, and keeps the default. The print is omitted
            # here: version.txt is a gitignored build artifact, so in the
            # Python port this branch is taken on every import (see
            # docs/porting_notes/T06.md).
            pass
        return version

    @staticmethod
    def parse_date_range(range_value: str) -> LongRange:
        """Java: Utilities#parseDateRange.

        Java overloads:
        (String range)

        Returns the commons-lang3 Range<Long> as a LongRange(minimum,
        maximum). IllegalArgumentException is mirrored as ValueError.
        Range.between sorts its endpoints, so a reversed range yields
        (high, low) rather than an error.
        """
        range_str = range_value
        first_dash = range_str.find("-")
        if (
            "-" not in range_str
            or len(range_str[:first_dash]) < 1
            or len(range_str[first_dash + 1 :]) < 1
        ):
            raise ValueError(f"Time range format error. Expect low-high. Found '{range_str}'")
        matcher = _DATE_RANGE_RE.match(range_str)
        if matcher:
            start = _local_date_to_epoch_milli(_parse_local_date(matcher.group(1)))
            end_date = _parse_local_date(matcher.group(2))
            end_days = _gregorian_days_from_civil(end_date.year, end_date.month, end_date.day) + 1
            end = end_days * 86400000 - 1
        else:
            start = parse_long(range_str[:first_dash])
            end = parse_long(range_str[first_dash + 1 :])
        return LongRange(min(start, end), max(start, end))

    @staticmethod
    def read_resource(
        filename: str, strip_bom: bool | None = None, allow_free_path: bool | None = None
    ) -> str:
        """Java: Utilities#readResource.

        Java overloads:
        (String filename) — classpath resource only.
        (String filename, boolean stripBOM, boolean allowFreePath)

        Classpath lookup is synthea.resources.resource_path(). A missing
        resource raises ValueError where Guava throws
        IllegalArgumentException; with allowFreePath, a missing resource
        falls back to reading the filename as a filesystem path.
        """
        strip = bool(strip_bom)
        free = bool(allow_free_path)
        # Guava's getResource treats the name as a classpath-relative
        # resource name; an absolute path is never a resource name (and
        # pathlib would otherwise resolve it as a plain file).
        path = resource_path(filename)
        if Path(filename).is_absolute():
            path = Path(filename) / "__not_a_resource__"
        if path.is_file():
            contents = path.read_bytes().decode("utf-8", errors="replace")
        elif not free:
            raise ValueError(f"resource {filename} not found.")
        else:
            contents = Path(filename).read_bytes().decode("utf-8", errors="replace")
        if strip and contents.startswith("\ufeff"):
            contents = contents[1:]
        return contents

    @staticmethod
    def read_resource_or_path(filename: str) -> str:
        """Java: Utilities#readResourceOrPath.

        Java overloads:
        (String filename)
        """
        return Utilities.read_resource(filename, False, True)

    @staticmethod
    def read_resource_and_strip_bom(filename: str) -> str:
        """Java: Utilities#readResourceAndStripBOM.

        Java overloads:
        (String filename)
        """
        return Utilities.read_resource(filename, True, False)

    @staticmethod
    def get_gson() -> Gson:
        """Java: Utilities#getGson.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: Utilities#getGson — out of scope for T06: the Gson "
            "configuration is bound to engine Logic/State type adapters "
            "(owned by the engine tasks); there is no Python Gson analogue."
        )

    @staticmethod
    def random_dicom_uid(
        random: RandomNumberGenerator, time: int, series_no: int, instance_no: int
    ) -> str:
        """Java: Utilities#randomDicomUid.

        Java overloads:
        (RandomNumberGenerator random, long time, int seriesNo, int instanceNo)

        Math.abs(Long.MIN_VALUE) is Long.MIN_VALUE in Java, so the "now"
        component can be negative; reproduced.
        """
        salt = Utilities.random_dicom_uid_salt(random)
        now = str(time if time == _LONG_MIN else abs(time))
        uid = "1.2.840.99999999"
        if series_no > 0:
            uid += "." + str(series_no)
        if instance_no > 0:
            uid += "." + str(instance_no)
        return uid + "." + salt + "." + now

    @staticmethod
    def random_dicom_uid_salt(random: RandomNumberGenerator) -> str:
        """Java: Utilities#randomDicomUidSalt (private in Java).

        Java overloads:
        (RandomNumberGenerator random)
        """
        min_salt = 10000000
        max_salt = 99999999
        salt_int = random.rand_int(max_salt - min_salt + 1) + min_salt
        return str(salt_int)

    @staticmethod
    def str_to_object(clazz: type[object] | str, value: str) -> object:
        """Java: Utilities#strToObject.

        Java overloads:
        (Class clazz, String value)

        ``clazz`` names the Java class: a Java class name ("Boolean",
        "java.lang.Byte", "int", ...) or the Python type bool/int/float
        (Boolean/Integer/Double). Byte/Short/Integer/Long parse as Java
        integral parses (ValueError on bad input or overflow), Float is
        parsed as a double then rounded to float32, and anything else
        raises ValueError (Java: IllegalArgumentException).
        """
        name = _java_target_name(clazz)
        match name:
            case "Boolean":
                return parse_boolean(value)
            case "Byte":
                return _parse_java_integral(value, -128, 127)
            case "Short":
                return _parse_java_integral(value, -32768, 32767)
            case "Integer":
                return parse_int(value)
            case "Long":
                return parse_long(value)
            case "Float":
                return struct.unpack("f", struct.pack("f", parse_double(value)))[0]
            case "Double":
                return parse_double(value)
            case _:
                raise ValueError(f"Cannot parse value for class {name}")

    @staticmethod
    def walk_all_modules(
        action_or_modules_path: BiConsumer | Path | Callable[[Path], None],
        action: Callable[[Path], None] | None = None,
    ) -> None:
        """Java: Utilities#walkAllModules.

        Java overloads:
        (BiConsumer action) — walks Module.getModulePaths() (engine).
        (Path modulesPath, Consumer action) — walks a directory tree and
            applies the action to every readable regular *.json file.
        """
        if action is None:
            raise NotImplementedError(
                "Java: Utilities#walkAllModules(BiConsumer) — out of scope "
                "for T06: the module roots come from engine Module "
                "(owned by the engine tasks)."
            )
        root = Path(action_or_modules_path)  # type: ignore[arg-type]
        for dirpath, _dirnames, filenames in _walk_files(root):
            for name in filenames:
                candidate = dirpath / name
                if candidate.is_file() and os_is_readable(candidate) and name.endswith(".json"):
                    action(candidate)

    @staticmethod
    def clean_map(input: dict[object, object]) -> dict[object, object]:
        """Java: Utilities#cleanMap — removes null-valued entries in place.

        Java overloads:
        (Map input)
        """
        keys_to_remove = [key for key in input if input[key] is None]
        for key in keys_to_remove:
            del input[key]
        return input

    @staticmethod
    def enable_reading_uri_from_jar(uri: URI | str) -> None:
        """Java: Utilities#enableReadingURIFromJar.

        Java overloads:
        (URI uri)

        A JDK jar-filesystem workaround. The Python port reads resources
        from plain files and never needs a jar filesystem, so — as in Java
        for every non-"jar" URI — this is a no-op (see porting notes).
        """
        return None

    @staticmethod
    def parse_yaml_to_resources[T: object](
        yaml: list[dict[str, object]], resource_class: type[T]
    ) -> list[T]:
        """Java: Utilities#parseYamlToResources.

        Java overloads:
        (List yaml, Class resourceClass)
        """
        raise NotImplementedError(
            "Java: Utilities#parseYamlToResources — out of scope for T06: "
            "FHIR resource parsing (owned by the FHIR export tasks)."
        )


def _java_pow(base: float, exponent: float) -> float:
    """Java: Math.pow — overflow yields +-Infinity and a negative base
    with a non-integral exponent yields NaN, where Python's math.pow
    raises OverflowError / ValueError instead."""
    try:
        return math.pow(base, exponent)
    except OverflowError:
        if base < 0 and exponent == math.floor(exponent) and int(exponent) % 2 == 1:
            return -math.inf
        return math.inf
    except ValueError:
        if base == 0.0 and exponent < 0:
            return math.inf
        return math.nan


def _walk_files(root: Path) -> list[tuple[Path, list[str], list[str]]]:
    """os.walk as a list (Files.walk is a depth-first directory stream)."""
    import os

    return [(Path(dp), dns, fns) for dp, dns, fns in os.walk(root)]


def os_is_readable(path: Path) -> bool:
    """Java: Files.isReadable."""
    import os

    return os.access(path, os.R_OK)


def _java_class_name(value: object) -> str:
    """The Java class name used in Utilities.compare's error message."""
    if isinstance(value, bool):
        return "java.lang.Boolean"
    if isinstance(value, int):
        return "java.lang.Integer"
    if isinstance(value, float):
        return "java.lang.Double"
    if isinstance(value, str):
        return "java.lang.String"
    if hasattr(value, "system") and hasattr(value, "code"):
        return "org.mitre.synthea.world.concepts.HealthRecord$Code"
    return type(value).__name__


def _java_target_name(clazz: type[object] | str) -> str:
    """Normalize a str_to_object class argument to a Java simple name."""
    if isinstance(clazz, str):
        simple = clazz.rsplit(".", 1)[-1]
        primitives = {
            "boolean": "Boolean",
            "byte": "Byte",
            "short": "Short",
            "int": "Integer",
            "long": "Long",
            "float": "Float",
            "double": "Double",
        }
        return primitives.get(simple, simple)
    if clazz is bool:
        return "Boolean"
    if clazz is int:
        return "Integer"
    if clazz is float:
        return "Double"
    return getattr(clazz, "__name__", str(clazz))


def _parse_java_integral(value: str, minimum: int, maximum: int) -> int:
    """Java Byte.parseByte / Short.parseShort (via the long parse + range)."""
    result = parse_long(value)
    if result < minimum or result > maximum:
        raise ValueError(f'For input string: "{value}"')
    return result


# Static initializer (Java: Utilities' SYNTHEA_VERSION field initializer).
Utilities.SYNTHEA_VERSION = Utilities.get_synthea_version()
