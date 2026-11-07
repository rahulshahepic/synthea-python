package org.synthea.parity.probes.support;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import org.mitre.synthea.world.agents.Payer;
import org.mitre.synthea.world.concepts.healthinsurance.CoverageRecord;
import org.mitre.synthea.world.concepts.healthinsurance.PlanRecord;

/**
 * Canonical CoverageRecord / PlanRecord dump for T16 parity
 * (see tests/parity/canonical/coverage.py for the byte-identical Python mirror).
 *
 * <p>Plan history lives in a Java HashSet whose iteration order is not part of
 * the behaviour under test, so records are sorted here by (start, stop, plan
 * id, payer name) — a total order for every history the probe can build.
 * BigDecimals and longs are rendered as strings (BigDecimal.toString /
 * Long.toString), matching the rest of the parity schema.
 */
public final class CanonicalCoverage {

  private CanonicalCoverage() { }

  /** Render one PlanRecord. */
  public static JsonObject planRecord(PlanRecord record) {
    JsonObject out = new JsonObject();
    out.addProperty("id", record.id);
    out.addProperty("start", Long.toString(record.getStartTime()));
    out.addProperty("stop", Long.toString(record.getStopTime()));
    out.addProperty("plan_id", record.getPlan().id);
    out.addProperty("payer", record.getPlan().getPayer().getName());
    out.addProperty(
        "secondary_plan_id",
        record.getSecondaryPlan() == null ? null : record.getSecondaryPlan().id);
    out.addProperty("ownership", record.ownership);
    out.addProperty("owner_name", record.ownerName);
    out.addProperty("remaining_deductible", record.remainingDeductible.toString());
    out.addProperty("covered", record.getCoveredExpenses().toString());
    out.addProperty("out_of_pocket", record.getOutOfPocketExpenses().toString());
    out.addProperty("insurance", record.getInsuranceExpenses().toString());
    out.addProperty("to_string", record.toString());
    return out;
  }

  /** Render one CoverageRecord (the owning Person is @JSONSkip in Java). */
  public static JsonObject coverage(CoverageRecord coverage) {
    JsonObject out = new JsonObject();
    List<PlanRecord> history = new ArrayList<>(coverage.getPlanHistory());
    history.sort(
        Comparator.comparingLong(PlanRecord::getStartTime)
            .thenComparingLong(PlanRecord::getStopTime)
            .thenComparingInt(record -> record.getPlan().id)
            .thenComparing(record -> record.getPlan().getPayer().getName()));
    JsonArray records = new JsonArray();
    for (PlanRecord record : history) {
      records.add(planRecord(record));
    }
    out.add("plan_history", records);
    out.addProperty("total_out_of_pocket", coverage.getTotalOutOfPocketExpenses().toString());
    out.addProperty("total_premium", coverage.getTotalPremiumExpenses().toString());
    out.addProperty("total_coverage", coverage.getTotalCoverage().toString());
    if (!history.isEmpty()) {
      out.addProperty(
          "last_plan_payer", coverage.getLastPlanRecord().getPlan().getPayer().getName());
    }
    return out;
  }

  /** Render a Payer's accumulated money/customer statistics. */
  public static JsonObject payerStats(Payer payer) {
    JsonObject out = new JsonObject();
    out.addProperty("name", payer.getName());
    out.addProperty("revenue", payer.getRevenue().toString());
    out.addProperty("amount_covered", payer.getAmountCovered().toString());
    out.addProperty("amount_uncovered", payer.getAmountUncovered().toString());
    out.addProperty("unique_customers", payer.getUniqueCustomers());
    out.addProperty("qols_average", Double.toString(payer.getQolsAverage()));
    return out;
  }
}
