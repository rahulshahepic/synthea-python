"""Support for the T20 StateProbe parity comparisons.

Mirrors parity/probes/org/synthea/parity/probes/StateProbe.java: every
top-level JSON module run for 20 scripted persons, with the outcome,
state history, canonical attributes, and a canonical health-record
summary (present entries, encounter count, symptom values) dumped
per person.

Two test forms use this support (AGENTS.md §4):

* integration (tests/parity/test_state.py): real code end to end.
  Modules whose runs call `EncounterModule.createEncounter` (T22,
  still a stub, and not a dependency #20 declares) cannot run here;
  they are exactly `ENCOUNTER_DEPENDENT_MODULES` below and are
  covered by the component form instead.
* component (tests/parity/test_state_component.py): every module,
  with `create_encounter_double` (tests/state_doubles.py) standing
  in for the T22 stub.
"""

from __future__ import annotations

from synthea.engine.module import Module, ModuleSupplier
from synthea.world.agents.person import Person
from tests.module_support import (
    _JAVA_EXCEPTION_NAMES,
    TIME,
    WEEK,
    _bool,
    canonical_value,
    scripted_person,
)

SEEDS = 20
MAX_STEPS = 200

# Modules in which at least one StateProbe run calls
# EncounterModule.createEncounter (T22): 94 modules, 1,880 of the
# 4,840 (module, seed) blocks (1,625 of those blocks raise the stub
# today; the rest run stub-free but stay with their module). All of
# their blocks are verified by the component form
# (tests/parity/test_state_component.py) with create_encounter_double.
# When T22 lands this set must empty and the counts asserted in
# tests/parity/test_state.py must be updated to cover every block in
# the integration form.
ENCOUNTER_DEPENDENT_MODULES: frozenset[str] = frozenset(
    {
        "allergies/allergy_panel",
        "allergies/immunotherapy",
        "allergies/severe_allergic_reaction",
        "anemia/anemia_sub",
        "breast_cancer/hormone_diagnosis",
        "breast_cancer/hormonetherapy_breast",
        "breast_cancer/surgery_therapy_breast",
        "breast_cancer/tnm_diagnosis",
        "bronchitis",
        "contraceptives/female_sterilization",
        "contraceptives/implant_contraceptive",
        "contraceptives/injectable_contraceptive",
        "contraceptives/intrauterine_device",
        "contraceptives/male_sterilization",
        "contraceptives/oral_contraceptive",
        "contraceptives/patch_contraceptive",
        "contraceptives/ring_contraceptive",
        "covid19",
        "covid19/admission",
        "covid19/infection",
        "covid19/measurements_daily",
        "covid19/measurements_frequent",
        "covid19/measurements_vitals",
        "covid19/supplies_hospitalization",
        "covid19/supplies_icu",
        "covid19/supplies_intubation",
        "covid19/symptoms",
        "dermatitis/early_moderate_eczema_obs",
        "dermatitis/early_severe_eczema_obs",
        "dermatitis/mid_moderate_eczema_obs",
        "dermatitis/mid_severe_eczema_obs",
        "dermatitis/moderate_cd_obs",
        "dermatitis/severe_cd_obs",
        "dme/wheelchair",
        "ear_infections",
        "encounter/anxiety_screening",
        "encounter/depression_screening",
        "encounter/hark_screening",
        "encounter/hospital_basic_labs",
        "encounter/sdoh_hrsn",
        "encounter/substance_use_screening",
        "eye/intraocular_pressure",
        "eye/ophthalmic_tomography",
        "eye/visual_acuity",
        "heart/avrr/avrr_referral",
        "heart/avrr/preoperative",
        "heart/avrr/savrr_operation",
        "heart/avrr/savrr_postop",
        "heart/avrr/sequence",
        "heart/cabg/cabg_referral",
        "heart/cabg/labs_common",
        "heart/cabg/operation",
        "heart/cabg/or_labs_meds",
        "heart/cabg/postop",
        "heart/cabg/preoperative",
        "heart/cabg_sequence",
        "heart/cardiac_labs",
        "heart/chf_lvad",
        "heart/chf_nyha_panel",
        "heart/chf_transplant",
        "heart/nsteacs_pathway",
        "heart/operative_status",
        "heart/savrepair/operative_status",
        "heart/savreplace/operative_status",
        "heart/stemi_pathway",
        "heart/tavr/alt_access",
        "heart/tavr/operation",
        "heart/tavr/operative_status",
        "heart/tavr/postop",
        "hiv/hiv_baseline",
        "hiv/hiv_cd4",
        "hiv/hiv_screening",
        "hiv/hiv_viral_load",
        "injuries",
        "injuries/broken_jaw",
        "metabolic_syndrome/amputations",
        "metabolic_syndrome/diabetic_retinopathy_diagnoses",
        "metabolic_syndrome/dme_supplies",
        "sinusitis",
        "snf/skilled_nursing_facility",
        "sore_throat",
        "surgery/general_anesthesia",
        "urinary_tract_infections",
        "uti/ambulatory_eval",
        "uti/ambulatory_path",
        "uti/ed_bundle",
        "uti/ed_eval",
        "uti/ed_path",
        "uti/gu_pregnancy_check",
        "uti/hpi",
        "uti/lab_follow_up",
        "uti/labs",
        "uti/telemed_path",
        "weight_loss/mend_week",
    }
)


def run_block(supplier: ModuleSupplier, seed: int) -> list[str]:
    """Mirror of StateProbe.runOne for one (module, seed): the block lines.

    A NotImplementedError from a production stub propagates (the
    integration test gates it through dependency_gate.run_or_pending);
    every other exception becomes the block's ERROR line, as in Java.
    """
    lines: list[str] = []
    person: Person = scripted_person(seed)
    module = supplier.get()
    time = TIME
    completed = False
    steps = 0
    try:
        while steps < MAX_STEPS:
            completed = module.process(person, time)
            steps += 1
            if completed:
                break
            time += WEEK
    except NotImplementedError:
        raise
    except Exception as e:  # Java: catch (RuntimeException)
        java_name = _JAVA_EXCEPTION_NAMES.get(type(e).__name__, type(e).__name__)
        lines.append(f"RUN|{supplier.path}|{seed}|ERROR|{java_name}")
        return lines
    lines.append(f"RUN|{supplier.path}|{seed}|completed={_bool(completed)}|steps={steps}")
    if person.history is not None:
        for i, state in enumerate(person.history):
            entered = "null" if state.entered is None else str(state.entered)
            exited = "null" if state.exited is None else str(state.exited)
            lines.append(f"H|{i}|{state.name}|{entered}|{exited}")
    for key in sorted(person.attributes.keys()):
        lines.append(f"A|{key}|{canonical_value(person.attributes.get(key))}")
    lines.append(f"E|{len(person.record.encounters)}")
    for key in sorted(person.record.present.keys()):
        entry = person.record.present[key]
        codes = ";".join(f"{c.system}:{c.code}:{c.display}" for c in entry.codes)
        name = "null" if entry.name is None else entry.name
        lines.append(f"R|{key}|{entry.type}|{name}|{entry.start}|{entry.stop}|{codes}")
    for symptom in sorted(person.get_symptoms()):
        lines.append(f"Y|{symptom}|{person.get_symptom(symptom)}")
    return lines


def probe_suppliers() -> list[ModuleSupplier]:
    """The suppliers StateProbe runs (non-core, with states)."""
    suppliers: list[ModuleSupplier] = []
    for supplier in Module.get_module_suppliers():
        if supplier.core:
            continue
        probe = supplier.get()
        if not probe.get_state_names():
            continue
        suppliers.append(supplier)
    return suppliers


def state_run_lines() -> list[str]:
    """Mirror of StateProbe.main (run.txt): every block, in order."""
    # NOTE: LookupTableTransition's static table cache is deliberately
    # NOT reset here. The Java probe's cache is filled by module loads
    # in registry order, which is what a Python process does naturally;
    # clearing it makes cloned modules' transitions reload tables in
    # run order and changes which instances carry `attributes`.
    lines: list[str] = []
    for supplier in probe_suppliers():
        for seed in range(SEEDS):
            lines.extend(run_block(supplier, seed))
    return lines


def blocks(lines: list[str]) -> dict[tuple[str, str], list[str]]:
    """Split probe output into (module path, seed) blocks."""
    out: dict[tuple[str, str], list[str]] = {}
    current: tuple[str, str] | None = None
    for line in lines:
        if line.startswith("RUN|"):
            parts = line.split("|")
            current = (parts[1], parts[2])
            out[current] = [line]
        elif current is not None:
            out[current].append(line)
    return out
