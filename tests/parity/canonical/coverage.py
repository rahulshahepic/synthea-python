"""Canonical CoverageRecord rendering, matching support/CanonicalCoverage.java.

Java: org.mitre.synthea.world.concepts.healthinsurance.CoverageRecord and
PlanRecord. Plan history lives in a Java HashSet whose iteration order is not
part of the behaviour under test, so records are sorted by (start, stop, plan
id, payer name) on both sides. BigDecimals and longs are strings
(BigDecimal.toString / Long.toString), as in the rest of the parity schema.
"""

from __future__ import annotations

from synthea.javacompat.bigdecimal import to_string
from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.payer import Payer
from synthea.world.concepts.healthinsurance.coverage_record import CoverageRecord
from synthea.world.concepts.healthinsurance.plan_record import PlanRecord


def dump_plan_record(record: PlanRecord) -> dict[str, object]:
    """Java: CanonicalCoverage.planRecord."""
    secondary = record.get_secondary_plan()
    return {
        "id": record.id,
        "start": str(record.get_start_time()),
        "stop": str(record.get_stop_time()),
        "plan_id": record.get_plan().id,
        "payer": record.get_plan().get_payer().get_name(),
        "secondary_plan_id": None if secondary is None else secondary.id,
        "ownership": record.ownership,
        "owner_name": record.owner_name,
        "remaining_deductible": to_string(record.remaining_deductible),
        "covered": to_string(record.get_covered_expenses()),
        "out_of_pocket": to_string(record.get_out_of_pocket_expenses()),
        "insurance": to_string(record.get_insurance_expenses()),
        "to_string": record.to_string(),
    }


def dump_coverage(coverage: CoverageRecord) -> dict[str, object]:
    """Java: CanonicalCoverage.coverage."""
    history = sorted(
        coverage.get_plan_history(),
        key=lambda record: (
            record.get_start_time(),
            record.get_stop_time(),
            record.get_plan().id,
            record.get_plan().get_payer().get_name(),
        ),
    )
    out: dict[str, object] = {
        "plan_history": [dump_plan_record(record) for record in history],
        "total_out_of_pocket": to_string(coverage.get_total_out_of_pocket_expenses()),
        "total_premium": to_string(coverage.get_total_premium_expenses()),
        "total_coverage": to_string(coverage.get_total_coverage()),
    }
    if history:
        out["last_plan_payer"] = coverage.get_last_plan_record().get_plan().get_payer().get_name()
    return out


def dump_payer_stats(payer: Payer) -> dict[str, object]:
    """Java: CanonicalCoverage.payerStats."""
    return {
        "name": payer.get_name(),
        "revenue": to_string(payer.get_revenue()),
        "amount_covered": to_string(payer.get_amount_covered()),
        "amount_uncovered": to_string(payer.get_amount_uncovered()),
        "unique_customers": payer.get_unique_customers(),
        "qols_average": double_to_string(payer.get_qols_average()),
    }
