package org.synthea.parity.probes.support;

import java.awt.geom.Point2D;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.mitre.synthea.engine.ExpressedConditionRecord;
import org.mitre.synthea.engine.ExpressedConditionRecord.ConditionPeriod;
import org.mitre.synthea.engine.ExpressedConditionRecord.ConditionWithSymptoms;
import org.mitre.synthea.engine.ExpressedConditionRecord.ModuleConditions;
import org.mitre.synthea.engine.ExpressedConditionRecord.OnsetCondition;
import org.mitre.synthea.engine.ExpressedSymptom;
import org.mitre.synthea.engine.ExpressedSymptom.SymptomSource;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.agents.Provider;
import org.mitre.synthea.world.concepts.HealthRecord;
import org.mitre.synthea.world.concepts.HealthRecord.Code;
import org.mitre.synthea.world.concepts.VitalSign;

/**
 * Canonical Person dump for T09 component parity (see tests/parity/canonical/person.py
 * for the byte-identical Python mirror). Everything order-sensitive is sorted here,
 * except where iteration order is itself the behaviour under test (those values are
 * produced by the Person API and appear as scalar results in the probe log).
 */
public final class CanonicalPerson {

  private CanonicalPerson() {}

  /** Render one attribute value (or nested value) canonically. */
  public static String renderValue(Object value) {
    if (value == null) {
      return "null";
    }
    if (value instanceof String) {
      return "str:" + value;
    }
    if (value instanceof Boolean) {
      return "bool:" + value;
    }
    if (value instanceof Long || value instanceof Integer) {
      return "int:" + value;
    }
    if (value instanceof Double) {
      return "double:" + Double.toString((Double) value);
    }
    if (value instanceof LocalDate) {
      return "date:" + value;
    }
    if (value instanceof Code) {
      Code code = (Code) value;
      return "code:" + code.system + "|" + code.code + "|" + code.display;
    }
    if (value instanceof Point2D.Double) {
      Point2D.Double point = (Point2D.Double) value;
      return "point:" + Double.toString(point.getX()) + "," + Double.toString(point.getY());
    }
    if (value instanceof Provider) {
      return "provider:" + ((Provider) value).getResourceID();
    }
    if (value instanceof java.time.Period) {
      return "period:" + value;
    }
    if (value instanceof Map) {
      Map<?, ?> map = (Map<?, ?>) value;
      List<String> keys = new ArrayList<>();
      for (Object key : map.keySet()) {
        keys.add(String.valueOf(key));
      }
      Collections.sort(keys);
      StringBuilder sb = new StringBuilder("map:{");
      boolean first = true;
      for (String key : keys) {
        if (!first) {
          sb.append(", ");
        }
        first = false;
        Object keyObject = null;
        for (Object candidate : map.keySet()) {
          if (String.valueOf(candidate).equals(key)) {
            keyObject = candidate;
            break;
          }
        }
        sb.append(key).append("=").append(renderValue(map.get(keyObject)));
      }
      return sb.append("}").toString();
    }
    if (value instanceof List) {
      StringBuilder sb = new StringBuilder("list:[");
      boolean first = true;
      for (Object element : (List<?>) value) {
        if (!first) {
          sb.append(", ");
        }
        first = false;
        sb.append(renderValue(element));
      }
      return sb.append("]").toString();
    }
    return "object:" + value.getClass().getSimpleName();
  }

  private static String nullable(Object value) {
    return value == null ? "null" : value.toString();
  }

  /** Full canonical dump of a Person's T09-owned state. */
  public static String dump(Person person) {
    StringBuilder sb = new StringBuilder();
    sb.append("seed=").append(person.getSeed()).append(" count=").append(person.getCount());
    sb.append("\nhasMultipleRecords=").append(person.hasMultipleRecords);
    sb.append("\nlossOfCareEnabled=").append(person.lossOfCareEnabled);
    sb.append("\nattributes:");
    List<String> attributeKeys = new ArrayList<>(person.attributes.keySet());
    Collections.sort(attributeKeys);
    for (String key : attributeKeys) {
      sb.append("\n  ").append(key).append(" = ").append(renderValue(person.attributes.get(key)));
    }
    sb.append("\nvitalSigns:");
    List<String> vitalNames = new ArrayList<>();
    for (VitalSign vitalSign : person.vitalSigns.keySet()) {
      vitalNames.add(vitalSign.name());
    }
    Collections.sort(vitalNames);
    for (String name : vitalNames) {
      sb.append("\n  ").append(name);
    }
    sb.append("\nsymptoms:");
    List<String> symptomTypes = new ArrayList<>(person.getExpressedSymptoms().keySet());
    Collections.sort(symptomTypes);
    for (String type : symptomTypes) {
      ExpressedSymptom symptom = person.getExpressedSymptoms().get(type);
      sb.append("\n  ").append(type)
          .append(": value=").append(symptom.getSymptom())
          .append(" high=").append(nullable(symptom.getSourceWithHighValue()));
      List<String> modules = new ArrayList<>(symptom.getSources().keySet());
      Collections.sort(modules);
      for (String module : modules) {
        SymptomSource source = symptom.getSources().get(module);
        sb.append("\n    ").append(module)
            .append(": resolved=").append(source.isResolved())
            .append(" last=").append(nullable(source.getLastUpdateTime()))
            .append(" current=").append(nullable(source.getCurrentValue()));
        List<Long> times = new ArrayList<>(source.getTimeInfos().keySet());
        Collections.sort(times);
        for (Long time : times) {
          sb.append("\n      ").append(time)
              .append(": cause=").append(source.getTimeInfos().get(time).getCause())
              .append(" value=").append(source.getTimeInfos().get(time).getValue());
        }
      }
    }
    sb.append("\nconditions:");
    ExpressedConditionRecord record = person.getOnsetConditionRecord();
    List<String> modules = new ArrayList<>(record.getSources().keySet());
    Collections.sort(modules);
    for (String module : modules) {
      ModuleConditions moduleConditions = record.getSources().get(module);
      sb.append("\n  ").append(module).append(":");
      List<String> conditions = new ArrayList<>(moduleConditions.getOnsetConditions().keySet());
      Collections.sort(conditions);
      for (String condition : conditions) {
        OnsetCondition onset = moduleConditions.getOnsetConditions().get(condition);
        sb.append("\n    ").append(condition).append(": periods=[");
        boolean first = true;
        for (ConditionPeriod period : onset.getTimeInfos()) {
          if (!first) {
            sb.append(", ");
          }
          first = false;
          sb.append(period.getOnsetTime()).append("..").append(nullable(period.getEndTime()));
        }
        sb.append("] lastOnset=").append(nullable(onset.getLastOnsetTime()))
            .append(" lastEnd=").append(nullable(onset.getLastEndTime()));
      }
    }
    sb.append("\nconditionSymptoms:");
    Map<Long, List<ConditionWithSymptoms>> conditionSymptoms = record.getConditionSymptoms();
    List<Long> begins = new ArrayList<>(conditionSymptoms.keySet());
    Collections.sort(begins);
    for (Long begin : begins) {
      sb.append("\n  ").append(begin).append(":");
      List<String> rendered = new ArrayList<>();
      for (ConditionWithSymptoms cws : conditionSymptoms.get(begin)) {
        StringBuilder entry = new StringBuilder();
        entry.append(cws.getConditionName())
            .append(" onset=").append(cws.getOnsetTime())
            .append(" end=").append(nullable(cws.getEndTime()))
            .append(" symptoms={");
        List<String> types = new ArrayList<>(cws.getSymptoms().keySet());
        Collections.sort(types);
        boolean first = true;
        for (String type : types) {
          if (!first) {
            entry.append(", ");
          }
          first = false;
          entry.append(type).append("=").append(cws.getSymptoms().get(type));
        }
        entry.append("}");
        rendered.add(entry.toString());
      }
      Collections.sort(rendered);
      for (String entry : rendered) {
        sb.append("\n    ").append(entry);
      }
    }
    sb.append("\nrecord: death=").append(nullable(person.record.death))
        .append(" provider=")
        .append(person.record.provider == null ? "null" : person.record.provider.getResourceID());
    if (person.hasMultipleRecords) {
      sb.append("\nrecords:");
      List<String> keys = new ArrayList<>(person.records.keySet());
      Collections.sort(keys);
      for (String key : keys) {
        HealthRecord healthRecord = person.records.get(key);
        sb.append("\n  ").append(key)
            .append(": provider=")
            .append(healthRecord.provider == null ? "null" : healthRecord.provider.getResourceID())
            .append(" death=").append(nullable(healthRecord.death));
      }
    }
    if (person.history != null) {
      sb.append("\nhistory: [");
      boolean first = true;
      for (org.mitre.synthea.engine.State state : person.history) {
        if (!first) {
          sb.append(", ");
        }
        first = false;
        sb.append(state.name).append("@").append(nullable(state.exited));
      }
      sb.append("]");
    }
    return sb.toString();
  }
}
