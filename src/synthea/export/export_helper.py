"""Java: org.mitre.synthea.export.ExportHelper."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from typing import TYPE_CHECKING, ClassVar

from synthea.engine.components import Attachment, SampledData
from synthea.javacompat import fmt as _fmt
from synthea.javacompat.hashing import string_hash_code
from synthea.javacompat.numbers import to_int64
from synthea.javacompat.uuid import java_uuid
from synthea.world.concepts.health_record import Code, Observation

if TYPE_CHECKING:
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person


class FhirCondition:
    """Java boundary type: org.hl7.fhir.dstu3.model.Condition.

    The port has no FHIR object model (FHIR export is out of scope, PORTING_GUIDE
    section 8), so no Python record ever holds one of these. The class exists so
    ExportHelper's instanceof branches keep their Java shape; tests may use it to
    stand on the boundary.
    """


_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)

# java.util.GregorianCalendar's default cutover: the first Gregorian day is
# 1582-10-15; earlier instants are formatted with Julian calendar rules.
_GREGORIAN_CUTOVER_MS = -12219292800000


def _civil_from_days_julian(z: int) -> tuple[int, int, int]:
    """(year, month, day) of a day count (days since 1970-01-01) in the Julian
    calendar, using March-based years (Hinnant's algorithm, 4-year eras)."""
    z += 719470
    era = z // 1461 if z >= 0 else (z - 1460) // 1461
    doe = z - era * 1461  # [0, 1460]
    yoe = (doe - doe // 1460) // 365  # [0, 3]
    year = yoe + era * 4
    doy = doe - 365 * yoe  # [0, 365]
    mp = (5 * doy + 2) // 153  # [0, 11]
    day = doy - (153 * mp + 2) // 5 + 1  # [1, 31]
    month = mp + 3 if mp < 10 else mp - 9  # [1, 12]
    return year + (1 if month <= 2 else 0), month, day


def _fields_from_millis(time_millis: int) -> tuple[int, int, int, int, int, int]:
    """(year, month, day, hour, minute, second) UTC for epoch millis, with the
    GregorianCalendar hybrid Julian/Gregorian cutover applied to the date."""
    if time_millis >= _GREGORIAN_CUTOVER_MS:
        dt = _EPOCH + timedelta(milliseconds=time_millis)
        return dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
    days, rem = divmod(time_millis, 86_400_000)
    year, month, day = _civil_from_days_julian(days)
    hour, rem = divmod(rem, 3_600_000)
    minute, rem = divmod(rem, 60_000)
    return year, month, day, hour, minute, rem // 1000


class _FastDateFormat:
    """Minimal stand-in for org.apache.commons.lang3.time.FastDateFormat.

    Supports the two patterns ExportHelper uses ("yyyy-MM-dd" and
    "yyyy-MM-dd'T'HH:mm:ss'Z'"). Java's DATE_FORMAT uses the JVM default time
    zone; the golden environment fixes that to UTC, and the port uses UTC
    everywhere (PORTING_GUIDE section 6).
    """

    def __init__(self, pattern: str) -> None:
        """Java: FastDateFormat#getInstance(String) — keep the pattern."""
        self.pattern = pattern

    def format(self, time_millis: int) -> str:
        """Java: FastDateFormat#format(Date) for a java.util.Date from millis."""
        year, month, day, hour, minute, second = _fields_from_millis(time_millis)
        out = self.pattern
        out = out.replace("'T'", "\x00").replace("'Z'", "\x01")
        out = out.replace("yyyy", f"{year:04d}")
        out = out.replace("MM", f"{month:02d}")
        out = out.replace("dd", f"{day:02d}")
        out = out.replace("HH", f"{hour:02d}")
        out = out.replace("mm", f"{minute:02d}")
        out = out.replace("ss", f"{second:02d}")
        return out.replace("\x00", "T").replace("\x01", "Z")


def _decimal_format(pattern: str | None) -> _DecimalFormatter:
    """Java: new java.text.DecimalFormat(pattern), or the default constructor."""
    if pattern is None:
        # DecimalFormat() default: pattern "#,##0.###" for the en-US locale.
        return _DecimalFormatter(min_int=1, grouping_size=3, min_frac=0, max_frac=3)
    int_part, _, frac_part = pattern.partition(".")
    grouping_size = 0
    if "," in int_part:
        grouping_size = len(int_part.rsplit(",", 1)[1].replace("#", "0"))
    return _DecimalFormatter(
        min_int=int_part.count("0"),
        grouping_size=grouping_size,
        min_frac=frac_part.count("0"),
        max_frac=len(frac_part),
    )


class _DecimalFormatter:
    """The subset of java.text.DecimalFormat behaviour ExportHelper needs.

    Java rounds the double's exact binary value with RoundingMode.HALF_EVEN
    (verified against the probe: 2.675 -> "2.67" at 2dp, 0.0005 -> "0.001" at
    3dp), so the digits come from Decimal(value), not the shortest repr.
    """

    def __init__(self, min_int: int, grouping_size: int, min_frac: int, max_frac: int) -> None:
        """Java: DecimalFormat's pattern-derived digit limits, pre-parsed."""
        self.min_int = min_int
        self.grouping_size = grouping_size
        self.min_frac = min_frac
        self.max_frac = max_frac

    def format(self, value: float) -> str:
        """Java: DecimalFormat#format(double)."""
        if value != value:  # NaN
            return "NaN"
        if value == float("inf"):
            return "∞"
        if value == float("-inf"):
            return "-∞"
        negative = value < 0 or (value == 0.0 and repr(value).startswith("-"))
        with localcontext() as ctx:
            ctx.prec = 80
            digits = Decimal(abs(value))
            quantum = Decimal(1).scaleb(-self.max_frac)
            rounded = digits.quantize(quantum, rounding=ROUND_HALF_EVEN)
        text = format(rounded, "f")
        int_text, _, frac_text = text.partition(".")
        frac_text = frac_text.ljust(self.max_frac, "0")
        while len(frac_text) > self.min_frac and frac_text.endswith("0"):
            frac_text = frac_text[:-1]
        int_text = int_text.rjust(self.min_int, "0")
        if self.grouping_size > 0:
            groups = []
            while len(int_text) > self.grouping_size:
                groups.append(int_text[-self.grouping_size :])
                int_text = int_text[: -self.grouping_size]
            groups.append(int_text)
            int_text = ",".join(reversed(groups))
        result = int_text
        if frac_text:
            result += "." + frac_text
        return ("-" if negative else "") + result


def _long_reverse(value: int) -> int:
    """Java: Long#reverse(long)."""
    bits = value & 0xFFFFFFFFFFFFFFFF
    return to_int64(int(format(bits, "064b")[::-1], 2))


def _long_rotate_left(value: int, distance: int) -> int:
    """Java: Long#rotateLeft(long, int); the distance is masked to 6 bits."""
    dist = distance & 63
    bits = value & 0xFFFFFFFFFFFFFFFF
    if dist == 0:
        return to_int64(bits)
    rotated = ((bits << dist) | (bits >> (64 - dist))) & 0xFFFFFFFFFFFFFFFF
    return to_int64(rotated)


def _java_to_string(value: object) -> str:
    """Java: Object#toString() for the value kinds an Observation can hold."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class ExportHelper:
    """Java: org.mitre.synthea.export.ExportHelper."""

    DATE_FORMAT: ClassVar[_FastDateFormat]
    ISO_DATE_FORMAT: ClassVar[_FastDateFormat]
    SNOMED_URI: ClassVar[str] = "http://snomed.info/sct"
    LOINC_URI: ClassVar[str] = "http://loinc.org"
    RXNORM_URI: ClassVar[str] = "http://www.nlm.nih.gov/research/umls/rxnorm"
    CVX_URI: ClassVar[str] = "http://hl7.org/fhir/sid/cvx"
    DICOM_DCM_URI: ClassVar[str] = (
        "http://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_29.html"
    )
    CDT_URI: ClassVar[str] = "http://www.ada.org/cdt"
    ICD9_URI: ClassVar[str] = "http://hl7.org/fhir/sid/icd-9-cm"
    ICD10_URI: ClassVar[str] = "http://hl7.org/fhir/sid/icd-10"
    ICD10_CM_URI: ClassVar[str] = "http://hl7.org/fhir/sid/icd-10-cm"
    CPT_URI: ClassVar[str] = "http://www.ama-assn.org/go/cpt"
    UNDUPLICATED_FHIR_RESOURCES: ClassVar[list[str]] = ["Location", "Organization", "Practitioner"]

    def __init__(self) -> None:
        """Java: ExportHelper#ExportHelper (abstract class; never instantiated)."""
        raise TypeError("Java: ExportHelper is abstract")

    @staticmethod
    def get_observation_value(observation: Observation, code: str | None = None) -> str | None:
        """Java: ExportHelper#getObservationValue.

        Java overloads:
        (Observation observation)
        (Observation observation, String code)
        """
        if code is not None:
            return ExportHelper._get_observation_value_by_code(observation, code)
        value = observation.value
        result: str | None = None
        if isinstance(value, FhirCondition):
            # Java casts the value to HealthRecord.Entry here; a FHIR Condition is
            # not an Entry, so Java always throws ClassCastException on this branch.
            raise TypeError(
                "Java ClassCastException: org.hl7.fhir.dstu3.model.Condition cannot be "
                "cast to org.mitre.synthea.world.concepts.HealthRecord$Entry"
            )
        elif isinstance(value, Code):
            result = value.display
        elif isinstance(value, str):
            result = value
        elif isinstance(value, float):
            # round to 1 decimal place for display
            result = _fmt.format("%.1f", value)
        elif isinstance(value, SampledData):
            result = ExportHelper.sampled_data_to_value_string(value)
        elif isinstance(value, Attachment):
            result = ExportHelper.attachment_to_value_string(value)
        elif value is not None:
            result = _java_to_string(value)
        return result

    @staticmethod
    def _get_observation_value_by_code(observation: Observation, code: str) -> str | None:
        """Java: ExportHelper#getObservationValue(Observation, String)."""
        # Check whether this observation has the desired code.
        for c in observation.codes:
            if c.code == code:
                return ExportHelper.get_observation_value(observation)
        # Check whether any of the contained observations have the desired code.
        for o in observation.observations:
            value = ExportHelper._get_observation_value_by_code(o, code)
            if value is not None:
                return value
        return None

    @staticmethod
    def sampled_data_to_value_string(sampled_data: SampledData) -> str:
        """Java: ExportHelper#sampledDataToValueString(SampledData)."""
        series_list = sampled_data.series
        if series_list is None:
            # Java throws NullPointerException here (series.get(0) on null).
            raise TypeError("Java NullPointerException: SampledData.series is null")
        num_samples = len(series_list[0].get_values())
        if sampled_data.decimal_format is not None:
            df = _decimal_format(sampled_data.decimal_format)
        else:
            df = _decimal_format(None)
        sb: list[str] = []
        for i in range(num_samples):
            for series in series_list:
                num = series.get_values()[i]
                sb.append(df.format(num))
                sb.append(" ")
        return "".join(sb).strip()

    @staticmethod
    def attachment_to_value_string(attachment: Attachment) -> str:
        """Java: ExportHelper#attachmentToValueString(Attachment)."""
        if attachment.data is not None:
            return attachment.data
        if attachment.url is not None:
            return attachment.url
        return ""

    @staticmethod
    def get_observation_type(observation: Observation) -> str | None:
        """Java: ExportHelper#getObservationType(Observation)."""
        value = observation.value
        result: str | None = None
        if isinstance(value, (FhirCondition, Code, str)):
            result = "text"
        elif isinstance(value, float):
            result = "numeric"
        elif isinstance(value, bool):
            result = "boolean"
        elif value is not None:
            result = "text"
        return result

    @staticmethod
    def iso() -> _FastDateFormat:
        """Java: ExportHelper#iso()."""
        return _FastDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'")

    @staticmethod
    def date_from_timestamp(time: int) -> str:
        """Java: ExportHelper#dateFromTimestamp(long)."""
        return ExportHelper.DATE_FORMAT.format(time)

    @staticmethod
    def iso8601_timestamp(time: int) -> str:
        """Java: ExportHelper#iso8601Timestamp(long)."""
        return ExportHelper.ISO_DATE_FORMAT.format(time)

    @staticmethod
    def next_friday(time: int) -> int:
        """Java: ExportHelper#nextFriday(long).

        Calendar (UTC) supplies the date; LocalDate.with(next(FRIDAY)) moves to
        the strictly-next Friday; the time of day is carried over unchanged.
        """
        dt = _EPOCH + timedelta(milliseconds=time)
        # Python weekday(): Monday=0 .. Friday=4 .. Sunday=6. next(FRIDAY) is
        # strictly after the current day, so a Friday maps to +7.
        days_ahead = (4 - dt.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target = dt + timedelta(days=days_ahead)
        delta = target - _EPOCH
        return delta.days * 86_400_000 + delta.seconds * 1000 + delta.microseconds // 1000

    @staticmethod
    def get_system_uri(system: str) -> str:
        """Java: ExportHelper#getSystemURI(String)."""
        lowered = system.lower()
        if lowered == "snomed-ct":
            system = ExportHelper.SNOMED_URI
        elif lowered == "loinc":
            system = ExportHelper.LOINC_URI
        elif lowered == "rxnorm":
            system = ExportHelper.RXNORM_URI
        elif lowered == "cvx":
            system = ExportHelper.CVX_URI
        elif lowered == "dicom-dcm":
            system = ExportHelper.DICOM_DCM_URI
        elif lowered == "cdt":
            system = ExportHelper.CDT_URI
        elif lowered == "icd9":
            system = ExportHelper.ICD9_URI
        elif lowered == "icd10":
            system = ExportHelper.ICD10_URI
        elif lowered == "icd10-cm":
            system = ExportHelper.ICD10_CM_URI
        elif lowered == "cpt":
            system = ExportHelper.CPT_URI
        return system

    @staticmethod
    def get_system_from_uri(uri: str) -> str:
        """Java: ExportHelper#getSystemFromURI(String)."""
        return {
            ExportHelper.SNOMED_URI: "SNOMED-CT",
            ExportHelper.LOINC_URI: "LOINC",
            ExportHelper.RXNORM_URI: "RxNorm",
            ExportHelper.CVX_URI: "CVX",
            ExportHelper.DICOM_DCM_URI: "DICOM-DCM",
            ExportHelper.CDT_URI: "CDT",
            ExportHelper.ICD9_URI: "ICD9",
            ExportHelper.ICD10_URI: "ICD10",
            ExportHelper.ICD10_CM_URI: "ICD10-CM",
            ExportHelper.CPT_URI: "CPT",
        }.get(uri, "Unknown")

    @staticmethod
    def build_fhir_search_url(resource_type: str, identifier: str) -> str:
        """Java: ExportHelper#buildFhirSearchUrl(String, String)."""
        return (
            resource_type
            + "?identifier="
            + "https://github.com/synthetichealth/synthea"
            + "|"
            + identifier
        )

    @staticmethod
    def build_fhir_npi_search_url(clinician: Clinician | None) -> str | None:
        """Java: ExportHelper#buildFhirNpiSearchUrl(Clinician)."""
        if clinician is None:
            return None
        return "Practitioner?identifier=" + "http://hl7.org/fhir/sid/us-npi" + "|" + clinician.npi

    @staticmethod
    def build_uuid(person_or_person_seed: Person | int, timestamp: int, key: str) -> str:
        """Java: ExportHelper#buildUUID.

        Java overloads:
        (Person person, long timestamp, String key)
        (long personSeed, long timestamp, String key)
        """
        if isinstance(person_or_person_seed, int):
            person_seed = person_or_person_seed
        else:
            person_seed = person_or_person_seed.get_seed()
        most_sig_bits = person_seed
        least_sig_bits = timestamp
        key_hash = string_hash_code(key)
        # first add the key to each long
        most_sig_bits = to_int64(most_sig_bits + key_hash)
        least_sig_bits = to_int64(least_sig_bits + key_hash)
        # reverse the hashCode to get the upper bits
        reversed_hash = _long_reverse(key_hash)
        most_sig_bits = to_int64(most_sig_bits + reversed_hash)
        least_sig_bits = to_int64(least_sig_bits + reversed_hash)
        # finally rotate the bits just to get a little more variance in the characters
        most_sig_bits = _long_rotate_left(most_sig_bits, key_hash)
        least_sig_bits = _long_rotate_left(least_sig_bits, key_hash)
        return java_uuid(most_sig_bits, least_sig_bits)


ExportHelper.DATE_FORMAT = _FastDateFormat("yyyy-MM-dd")
ExportHelper.ISO_DATE_FORMAT = ExportHelper.iso()
