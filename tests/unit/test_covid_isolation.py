"""#84: a COVID parity run leaves the process globals exactly as it found them."""

from __future__ import annotations

from synthea.engine.module import Module
from synthea.helpers.config import Config
from synthea.modules.covid.c19_vaccine import C19Vaccine
from synthea.modules.covid.c19_vaccine_age_distributions import C19VaccineAgeDistributions
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.provider import Provider
from tests.covid_support import isolated_globals, reset_covid_statics, setup_process_runtime


def test_isolated_globals_restores_what_a_covid_run_loads() -> None:
    before = {
        "providers": Provider.providerByUuid,
        "provider_count": len(Provider.providerByUuid),
        "provider_states": set(Provider.statesLoaded),
        "provider_map": Provider.providerMap,
        "payers": PayerManager.payers,
        "payer_count": len(PayerManager.payers),
        "modules": Module.modules,
        "distributions": C19VaccineAgeDistributions.distributions,
        "euas": C19Vaccine.EUAs,
        "config": Config.properties,
    }
    with isolated_globals():
        reset_covid_statics()
        setup_process_runtime()
        Provider.clear()  # in place, as the production code and older fixtures do
        PayerManager.clear()
        Config.set("isolation.probe", "1")
    assert Provider.providerByUuid is before["providers"]
    assert len(Provider.providerByUuid) == before["provider_count"]
    assert Provider.statesLoaded == before["provider_states"]
    assert Provider.providerMap is before["provider_map"]
    assert PayerManager.payers is before["payers"]
    assert len(PayerManager.payers) == before["payer_count"]
    assert Module.modules is before["modules"]
    assert C19VaccineAgeDistributions.distributions is before["distributions"]
    assert C19Vaccine.EUAs is before["euas"]
    assert Config.properties is before["config"]
    assert "isolation.probe" not in Config.properties
