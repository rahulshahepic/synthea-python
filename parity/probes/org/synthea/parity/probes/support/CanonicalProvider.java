package org.synthea.parity.probes.support;

import com.google.common.collect.Table;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.mitre.synthea.world.agents.Clinician;
import org.mitre.synthea.world.agents.Provider;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;

/**
 * Canonical Provider/Clinician dump for T13 parity (see
 * tests/parity/canonical/provider.py for the byte-identical Python mirror).
 * Everything order-sensitive is sorted here (attribute keys, services,
 * specialties, utilization cells), except the provider list order itself and
 * the clinician order within a specialty, which are the behaviour under test
 * (Provider#getProviderList iterates the backing HashMap; clinician lists are
 * generated in order).
 */
public final class CanonicalProvider {

  private CanonicalProvider() {}

  private static String nullable(Object value) {
    return value == null ? "null" : value.toString();
  }

  /** Canonical dump of one clinician (no leading indent on the first line). */
  public static String dumpClinician(Clinician clinician) {
    StringBuilder sb = new StringBuilder();
    sb.append("clinician: uuid=").append(clinician.uuid)
        .append(" identifier=").append(clinician.identifier)
        .append(" npi=").append(nullable(clinician.npi))
        .append(" org=")
        .append(clinician.getOrganization() == null
            ? "null" : clinician.getOrganization().getResourceID())
        .append(" encounters=").append(clinician.getEncounterCount())
        .append(" procedures=").append(clinician.getProcedureCount())
        .append(" populationSeed=").append(clinician.populationSeed)
        .append(" fullname=").append(clinician.getFullname());
    sb.append("\n  clinServices: wellness=").append(clinician.hasService(Clinician.WELLNESS))
        .append(" ambulatory=").append(clinician.hasService(Clinician.AMBULATORY))
        .append(" inpatient=").append(clinician.hasService(Clinician.INPATIENT))
        .append(" emergency=").append(clinician.hasService(Clinician.EMERGENCY))
        .append(" urgentcare=").append(clinician.hasService(Clinician.URGENTCARE));
    sb.append("\n  clinAttributes:");
    List<String> keys = new ArrayList<>(clinician.attributes.keySet());
    Collections.sort(keys);
    for (String key : keys) {
      sb.append("\n    ").append(key).append(" = ")
          .append(CanonicalPerson.renderValue(clinician.attributes.get(key)));
    }
    return sb.toString();
  }

  /** Full canonical dump of a Provider's T13-owned state. */
  public static String dump(Provider provider) {
    StringBuilder sb = new StringBuilder();
    sb.append("provider: uuid=").append(provider.uuid)
        .append(" locationUuid=").append(provider.getResourceLocationID())
        .append(" id=").append(nullable(provider.id))
        .append(" npi=").append(nullable(provider.npi))
        .append(" name=").append(nullable(provider.name))
        .append(" type=").append(provider.type == null ? "null" : provider.type.name())
        .append(" institutional=").append(provider.institutional)
        .append(" bedCount=").append(nullable(provider.bedCount))
        .append(" revenue=").append(Double.toString(provider.getRevenue()))
        .append(" coordinates=")
        .append(Double.toString(provider.getLonLat().getX()))
        .append(",")
        .append(Double.toString(provider.getLonLat().getY()));
    sb.append("\ncms: providerNum=").append(nullable(provider.cmsProviderNum))
        .append(" pin=").append(nullable(provider.cmsPin))
        .append(" upin=").append(nullable(provider.cmsUpin))
        .append(" category=").append(nullable(provider.cmsCategory))
        .append(" providerType=").append(nullable(provider.cmsProviderType))
        .append(" region=").append(nullable(provider.cmsRegion))
        .append(" clia=").append(nullable(provider.cliaNumber));
    sb.append("\nplace: address=").append(nullable(provider.address))
        .append(" city=").append(nullable(provider.city))
        .append(" state=").append(nullable(provider.state))
        .append(" zip=").append(nullable(provider.zip))
        .append(" fips=").append(nullable(provider.fipsCountyCode))
        .append(" phone=").append(nullable(provider.phone))
        .append(" ownership=").append(nullable(provider.ownership));
    List<String> services = new ArrayList<>();
    for (EncounterType service : provider.servicesProvided) {
      services.add(service.name());
    }
    Collections.sort(services);
    sb.append("\nservices: [").append(String.join(", ", services)).append("]");
    sb.append("\nattributes:");
    List<String> attributeKeys = new ArrayList<>(provider.attributes.keySet());
    Collections.sort(attributeKeys);
    for (String key : attributeKeys) {
      sb.append("\n  ").append(key).append(" = ")
          .append(CanonicalPerson.renderValue(provider.attributes.get(key)));
    }
    List<Table.Cell<Integer, String, AtomicInteger>> cells =
        new ArrayList<>(provider.getUtilization().cellSet());
    cells.sort((left, right) -> {
      int byYear = Integer.compare(left.getRowKey(), right.getRowKey());
      return byYear != 0 ? byYear : left.getColumnKey().compareTo(right.getColumnKey());
    });
    List<String> renderedCells = new ArrayList<>();
    for (Table.Cell<Integer, String, AtomicInteger> cell : cells) {
      renderedCells.add(cell.getRowKey() + "|" + cell.getColumnKey() + "|" + cell.getValue().get());
    }
    sb.append("\nutilization: [").append(String.join(", ", renderedCells)).append("]");
    sb.append("\nclinicians:");
    List<String> specialties = new ArrayList<>(provider.clinicianMap.keySet());
    Collections.sort(specialties);
    for (String specialty : specialties) {
      sb.append("\n  ").append(specialty).append(":");
      for (Clinician clinician : provider.clinicianMap.get(specialty)) {
        sb.append("\n    ").append(dumpClinician(clinician).replace("\n", "\n    "));
      }
    }
    return sb.toString();
  }
}
