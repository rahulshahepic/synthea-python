package org.synthea.parity.probes;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.lang.reflect.Array;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/** Java reference data for the T04 API skeleton; no simulation methods are invoked. */
public class SkeletonProbe {
  private static final String[] DATA_CLASSES = {
    "org.mitre.synthea.world.agents.Person",
    "org.mitre.synthea.world.concepts.ClinicianSpecialty",
    "org.mitre.synthea.world.concepts.HealthRecord",
    "org.mitre.synthea.world.concepts.RaceAndEthnicity",
    "org.mitre.synthea.world.concepts.Claim",
    "org.mitre.synthea.helpers.Telemedicine",
    "org.mitre.synthea.engine.ReactionProbabilities",
    "org.mitre.synthea.modules.calculators.ASCVD",
    "org.mitre.synthea.modules.calculators.Framingham",
    "org.mitre.synthea.export.CSVConstants"
  };

  private static final String[] API_CLASSES = {
    "org.mitre.synthea.helpers.Config",
    "org.mitre.synthea.helpers.SimpleCSV",
    "org.mitre.synthea.helpers.SimpleYML",
    "org.mitre.synthea.helpers.Utilities",
    "org.mitre.synthea.helpers.TimeSeriesData",
    "org.mitre.synthea.helpers.Telemedicine",
    "org.mitre.synthea.helpers.RandomCollection",
    "org.mitre.synthea.helpers.SyncedEnumeratedDistro",
    "org.mitre.synthea.engine.Distribution",
    "org.mitre.synthea.helpers.ValueGenerator",
    "org.mitre.synthea.helpers.ConstantValueGenerator",
    "org.mitre.synthea.helpers.RandomValueGenerator",
    "org.mitre.synthea.helpers.TrendingValueGenerator",
    "org.mitre.synthea.helpers.RandomCodeGenerator",
    "org.mitre.synthea.helpers.ExpressionProcessor",
    "org.mitre.synthea.world.concepts.HealthRecord",
    "org.mitre.synthea.world.agents.Person",
    "org.mitre.synthea.engine.ExpressedSymptom",
    "org.mitre.synthea.engine.ExpressedConditionRecord",
    "org.mitre.synthea.world.geography.Place",
    "org.mitre.synthea.world.geography.Location",
    "org.mitre.synthea.world.geography.Demographics",
    "org.mitre.synthea.world.geography.CMSStateCodeMapper",
    "org.mitre.synthea.world.geography.quadtree.QuadTree",
    "org.mitre.synthea.world.geography.quadtree.QuadTreeElement",
    "org.mitre.synthea.world.concepts.Employment",
    "org.mitre.synthea.world.concepts.Names",
    "org.mitre.synthea.world.concepts.RaceAndEthnicity",
    "org.mitre.synthea.world.concepts.ClinicianSpecialty",
    "org.mitre.synthea.world.concepts.VitalSign",
    "org.mitre.synthea.world.concepts.BiometricsConfig",
    "org.mitre.synthea.world.concepts.TelemedicineConfig",
    "org.mitre.synthea.world.concepts.BMI",
    "org.mitre.synthea.world.concepts.BirthStatistics",
    "org.mitre.synthea.world.concepts.GrowthChart",
    "org.mitre.synthea.world.concepts.GrowthChartEntry",
    "org.mitre.synthea.world.concepts.NHANESSample",
    "org.mitre.synthea.world.concepts.PediatricGrowthTrajectory",
    "org.mitre.synthea.world.agents.Clinician",
    "org.mitre.synthea.world.agents.Provider",
    "org.mitre.synthea.world.agents.behaviors.providerfinder.IProviderFinder",
    "org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderNearest",
    "org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderNearestMedicare",
    "org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderRandom",
    "org.mitre.synthea.world.concepts.Costs",
    "org.mitre.synthea.world.concepts.Claim",
    "org.mitre.synthea.world.agents.Payer",
    "org.mitre.synthea.world.agents.PayerManager",
    "org.mitre.synthea.world.concepts.healthinsurance.InsurancePlan",
    "org.mitre.synthea.world.agents.behaviors.payeradjustment.IPayerAdjustment",
    "org.mitre.synthea.world.agents.behaviors.payeradjustment.PayerAdjustmentFixed",
    "org.mitre.synthea.world.agents.behaviors.payeradjustment.PayerAdjustmentNone",
    "org.mitre.synthea.world.agents.behaviors.payeradjustment.PayerAdjustmentRandom",
    "org.mitre.synthea.world.agents.behaviors.planfinder.IPlanFinder",
    "org.mitre.synthea.world.agents.behaviors.planfinder.PlanFinderBestRates",
    "org.mitre.synthea.world.agents.behaviors.planfinder.PlanFinderPriority",
    "org.mitre.synthea.world.agents.behaviors.planfinder.PlanFinderRandom",
    "org.mitre.synthea.world.concepts.healthinsurance.PlanRecord",
    "org.mitre.synthea.world.concepts.healthinsurance.CoverageRecord",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.IPlanEligibility",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.DefaultPlanEligibility",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.PlanEligibilityFinder",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.IncomeSpenddownEligibility",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.PovertyMultiplierFileEligibility",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.QualifyingAttributesEligibility",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.QualifyingConditionCodesEligibility",
    "org.mitre.synthea.modules.HealthInsuranceModule",
    "org.mitre.synthea.engine.Components",
    "org.mitre.synthea.engine.Logic",
    "org.mitre.synthea.engine.Transition",
    "org.mitre.synthea.engine.Module",
    "org.mitre.synthea.engine.State",
    "org.mitre.synthea.engine.ReactionProbabilities",
    "org.mitre.synthea.modules.LifecycleModule",
    "org.mitre.synthea.modules.BloodPressureValueGenerator",
    "org.mitre.synthea.modules.EncounterModule",
    "org.mitre.synthea.modules.DeathModule",
    "org.mitre.synthea.modules.Immunizations",
    "org.mitre.synthea.modules.CardiovascularDiseaseModule",
    "org.mitre.synthea.modules.calculators.ASCVD",
    "org.mitre.synthea.modules.calculators.Framingham",
    "org.mitre.synthea.modules.QualityOfLifeModule",
    "org.mitre.synthea.modules.WeightLossModule",
    "org.mitre.synthea.modules.covid.C19ImmunizationModule",
    "org.mitre.synthea.modules.covid.C19Vaccine",
    "org.mitre.synthea.modules.covid.C19VaccineAgeDistributions",
    "org.mitre.synthea.modules.covid.LateAdopterModel",
    "org.mitre.synthea.export.Exporter",
    "org.mitre.synthea.export.ExportHelper",
    "org.mitre.synthea.export.CSVFileManager",
    "org.mitre.synthea.export.CSVConstants",
    "org.mitre.synthea.export.CSVExporter",
    "org.mitre.synthea.engine.Generator",
    "App",
    "org.mitre.synthea.world.agents.behaviors.planeligibility.CSVEligibility"
  };

  /** Keep decimals exact, map order immaterial, and arrays recursive. */
  private static Object canonical(Object value) {
    if (value instanceof BigDecimal decimal) {
      return decimal.toPlainString();
    }
    if (value instanceof Map<?, ?> map) {
      Map<String, Object> result = new TreeMap<>();
      map.forEach((key, item) -> result.put(String.valueOf(key), canonical(item)));
      return result;
    }
    if (value != null && value.getClass().isArray()) {
      List<Object> result = new ArrayList<>();
      for (int i = 0; i < Array.getLength(value); i++) {
        result.add(canonical(Array.get(value, i)));
      }
      return result;
    }
    return value;
  }

  /** Reflect declarations without initializing runtime configuration or invoking stubs. */
  private static void describe(Class<?> type, Map<String, Object> output) {
    Map<String, Object> api = new TreeMap<>();
    Map<String, Object> methods = new TreeMap<>();
    for (java.lang.reflect.Method method : type.getDeclaredMethods()) {
      if (method.isSynthetic() || (type.isEnum()
          && (method.getName().equals("values") || method.getName().equals("valueOf")))) {
        continue;
      }
      Map<String, Object> signature = new TreeMap<>();
      signature.put("arity", method.getParameterCount());
      signature.put("static", Modifier.isStatic(method.getModifiers()));
      methods.put(method.getName() + "/" + method.toGenericString(), signature);
    }
    List<Integer> constructors = new ArrayList<>();
    if (!type.isEnum() && !type.isInterface()) {
      for (java.lang.reflect.Constructor<?> constructor : type.getDeclaredConstructors()) {
        if (constructor.isSynthetic()) {
          continue;
        }
        int hiddenOuter = type.isMemberClass() && !Modifier.isStatic(type.getModifiers()) ? 1 : 0;
        constructors.add(constructor.getParameterCount() - hiddenOuter);
      }
    }
    java.util.Collections.sort(constructors);
    api.put("methods", methods);
    api.put("constructors", constructors);
    api.put("enum", type.isEnum());
    api.put("interface", type.isInterface());
    output.put(type.getName(), api);
    for (Class<?> nested : type.getDeclaredClasses()) {
      if (!nested.isSynthetic()) {
        describe(nested, output);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    Map<String, Object> output = new TreeMap<>();
    for (String className : DATA_CLASSES) {
      Class<?> type = Class.forName(className);
      Map<String, Object> fields = new TreeMap<>();
      for (Field field : type.getDeclaredFields()) {
        if (Modifier.isStatic(field.getModifiers()) && !field.isSynthetic()) {
          field.setAccessible(true);
          fields.put(field.getName(), canonical(field.get(null)));
        }
      }
      output.put(className, fields);
    }
    for (String className : new String[] {
        "org.mitre.synthea.world.concepts.HealthRecord$EncounterType",
        "org.mitre.synthea.world.concepts.HealthRecord$ReactionSeverity",
        "org.mitre.synthea.world.concepts.VitalSign"
    }) {
      Class<?> type = Class.forName(className);
      Map<String, Object> members = new TreeMap<>();
      for (Object member : type.getEnumConstants()) {
        Map<String, Object> fields = new TreeMap<>();
        for (Field field : type.getDeclaredFields()) {
          if (!Modifier.isStatic(field.getModifiers()) && !field.isSynthetic()) {
            field.setAccessible(true);
            fields.put(field.getName(), canonical(field.get(member)));
          }
        }
        members.put(((Enum<?>) member).name(), fields);
      }
      output.put(className, members);
    }
    Map<String, Object> api = new TreeMap<>();
    for (String className : API_CLASSES) {
      describe(Class.forName(className, false, SkeletonProbe.class.getClassLoader()), api);
    }
    Gson gson = new GsonBuilder().serializeNulls().setPrettyPrinting().create();
    Files.writeString(Path.of(args[0]).resolve("api.json"),
        gson.toJson(api) + "\n", StandardCharsets.UTF_8);
    Files.writeString(Path.of(args[0]).resolve("constants.json"),
        gson.toJson(output) + "\n", StandardCharsets.UTF_8);
  }
}
