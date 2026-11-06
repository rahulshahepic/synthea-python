"""Canonical Person dumps for T09 parity (mirror of CanonicalPerson.java).

Byte-identical Python mirror of
``parity/probes/org/synthea/parity/probes/support/CanonicalPerson.java``.
Everything order-sensitive is sorted, except where iteration order is itself
the behaviour under test (those values are produced by the Person API and
appear as scalar results in the probe log).
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.person import Period, Point2DDouble

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


def _nullable(value: object) -> str:
    """Java: value == null ? "null" : value.toString()."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_value(value: object) -> str:
    """Mirror of CanonicalPerson.renderValue."""
    if value is None:
        return "null"
    if isinstance(value, str):
        return "str:" + value
    if isinstance(value, bool):
        return "bool:" + ("true" if value else "false")
    if isinstance(value, int):
        return "int:" + str(value)
    if isinstance(value, float):
        return "double:" + double_to_string(value)
    if isinstance(value, date):
        return "date:" + value.isoformat()
    if isinstance(value, Period):
        return "period:" + str(value)
    if isinstance(value, Point2DDouble):
        return "point:" + double_to_string(value.get_x()) + "," + double_to_string(value.get_y())
    # HealthRecord.Code (T08) and the component-test doubles carry these fields.
    if hasattr(value, "system") and hasattr(value, "code") and hasattr(value, "display"):
        return f"code:{value.system}|{value.code}|{value.display}"  # type: ignore[attr-defined]
    if hasattr(value, "uuid") and hasattr(value, "get_resource_id"):
        return "provider:" + str(value.get_resource_id())  # type: ignore[attr-defined]
    if isinstance(value, dict) or hasattr(value, "items"):
        items = list(value.items())  # type: ignore[attr-defined]
        rendered_keys = sorted(str(key) for key, _ in items)
        by_rendered = {str(key): val for key, val in items}
        parts = [f"{key}={render_value(by_rendered[key])}" for key in rendered_keys]
        return "map:{" + ", ".join(parts) + "}"
    if isinstance(value, (list, tuple)):
        return "list:[" + ", ".join(render_value(element) for element in value) + "]"
    return "object:" + type(value).__name__


def dump(person: Person) -> str:
    """Mirror of CanonicalPerson.dump."""
    lines: list[str] = []
    lines.append(f"seed={person.get_seed()} count={person.get_count()}")
    lines.append(f"hasMultipleRecords={_nullable(person.has_multiple_records)}")
    lines.append(f"lossOfCareEnabled={_nullable(person.loss_of_care_enabled)}")
    lines.append("attributes:")
    for key in sorted(person.attributes):
        lines.append(f"  {key} = {render_value(person.attributes[key])}")
    lines.append("vitalSigns:")
    for name in sorted(vital_sign.name for vital_sign in person.vital_signs):
        lines.append(f"  {name}")
    lines.append("symptoms:")
    symptoms = person.get_expressed_symptoms()
    for type_name in sorted(symptoms):
        symptom = symptoms[type_name]
        lines.append(
            f"  {type_name}: value={symptom.get_symptom()}"
            f" high={_nullable(symptom.get_source_with_high_value())}"
        )
        for module in sorted(symptom.get_sources()):
            source = symptom.get_sources()[module]
            lines.append(
                f"    {module}: resolved={_nullable(source.is_resolved())}"
                f" last={_nullable(source.get_last_update_time())}"
                f" current={_nullable(source.get_current_value())}"
            )
            for time in sorted(source.get_time_infos()):
                info = source.get_time_infos()[time]
                lines.append(
                    f"      {time}: cause={info.get_cause()} value={_nullable(info.get_value())}"
                )
    lines.append("conditions:")
    record = person.get_onset_condition_record()
    for module in sorted(record.get_sources()):
        module_conditions = record.get_sources()[module]
        lines.append(f"  {module}:")
        for condition in sorted(module_conditions.get_onset_conditions()):
            onset = module_conditions.get_onset_conditions()[condition]
            periods = ", ".join(
                f"{period.get_onset_time()}..{_nullable(period.get_end_time())}"
                for period in onset.get_time_infos()
            )
            lines.append(
                f"    {condition}: periods=[{periods}]"
                f" lastOnset={_nullable(onset.get_last_onset_time())}"
                f" lastEnd={_nullable(onset.get_last_end_time())}"
            )
    lines.append("conditionSymptoms:")
    condition_symptoms = record.get_condition_symptoms()
    for begin in sorted(condition_symptoms):
        lines.append(f"  {begin}:")
        rendered: list[str] = []
        for cws in condition_symptoms[begin]:
            parts: list[str] = []
            for type_name in sorted(cws.get_symptoms()):
                values = cws.get_symptoms()[type_name]
                parts.append(f"{type_name}=[{', '.join(_nullable(v) for v in values)}]")
            rendered.append(
                f"{cws.get_condition_name()} onset={cws.get_onset_time()}"
                f" end={_nullable(cws.get_end_time())} symptoms={{{', '.join(parts)}}}"
            )
        for entry in sorted(rendered):
            lines.append(f"    {entry}")
    record_obj = person.record
    death = record_obj.death if record_obj is not None else None
    provider = record_obj.provider if record_obj is not None else None
    provider_id = provider.get_resource_id() if provider is not None else "null"
    lines.append(f"record: death={_nullable(death)} provider={provider_id}")
    if person.has_multiple_records:
        lines.append("records:")
        records = person.records
        if records is not None:
            for key in sorted(records):
                health_record = records[key]
                rec_provider = health_record.provider
                rec_provider_id = (
                    rec_provider.get_resource_id() if rec_provider is not None else "null"
                )
                lines.append(
                    f"  {key}: provider={rec_provider_id} death={_nullable(health_record.death)}"
                )
    if person.history is not None:
        history = ", ".join(f"{state.name}@{_nullable(state.exited)}" for state in person.history)
        lines.append(f"history: [{history}]")
    return "\n".join(lines)
