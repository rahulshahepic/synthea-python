"""Canonical Provider/Clinician dumps for T13 parity.

Byte-identical Python mirror of
``parity/probes/org/synthea/parity/probes/support/CanonicalProvider.java``.
Everything order-sensitive is sorted, except the provider list order itself
and the clinician order within a specialty, which are the behaviour under
test.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.clinician import Clinician
from tests.parity.canonical.person import render_value

if TYPE_CHECKING:
    from synthea.world.agents.provider import Provider


def _nullable(value: object) -> str:
    """Java: value == null ? "null" : value.toString()."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _b(value: bool) -> str:
    """Java: Boolean.toString."""
    return "true" if value else "false"


def dump_clinician(clinician: Clinician) -> str:
    """Mirror of CanonicalProvider.dumpClinician."""
    organization = clinician.get_organization()
    org_id = "null" if organization is None else organization.get_resource_id()
    lines = [
        f"clinician: uuid={clinician.uuid}"
        f" identifier={clinician.identifier}"
        f" npi={_nullable(clinician.npi)}"
        f" org={org_id}"
        f" encounters={clinician.get_encounter_count()}"
        f" procedures={clinician.get_procedure_count()}"
        f" populationSeed={clinician.population_seed}"
        f" fullname={clinician.get_fullname()}",
        f"  clinServices: wellness={_b(clinician.has_service(Clinician.WELLNESS))}"
        f" ambulatory={_b(clinician.has_service(Clinician.AMBULATORY))}"
        f" inpatient={_b(clinician.has_service(Clinician.INPATIENT))}"
        f" emergency={_b(clinician.has_service(Clinician.EMERGENCY))}"
        f" urgentcare={_b(clinician.has_service(Clinician.URGENTCARE))}",
        "  clinAttributes:",
    ]
    for key in sorted(clinician.attributes):
        lines.append(f"    {key} = {render_value(clinician.attributes[key])}")
    return "\n".join(lines)


def dump(provider: Provider) -> str:
    """Mirror of CanonicalProvider.dump."""
    lon_lat = provider.get_lon_lat()
    lines = [
        f"provider: uuid={provider.uuid}"
        f" locationUuid={provider.get_resource_location_id()}"
        f" id={_nullable(provider.id)}"
        f" npi={_nullable(provider.npi)}"
        f" name={_nullable(provider.name)}"
        f" type={provider.type.name if provider.type is not None else 'null'}"
        f" institutional={_b(provider.institutional)}"
        f" bedCount={_nullable(provider.bed_count)}"
        f" revenue={double_to_string(provider.get_revenue())}"
        f" coordinates={double_to_string(lon_lat.get_x())},{double_to_string(lon_lat.get_y())}",
        f"cms: providerNum={_nullable(provider.cms_provider_num)}"
        f" pin={_nullable(provider.cms_pin)}"
        f" upin={_nullable(provider.cms_upin)}"
        f" category={_nullable(provider.cms_category)}"
        f" providerType={_nullable(provider.cms_provider_type)}"
        f" region={_nullable(provider.cms_region)}"
        f" clia={_nullable(provider.clia_number)}",
        f"place: address={_nullable(provider.address)}"
        f" city={_nullable(provider.city)}"
        f" state={_nullable(provider.state)}"
        f" zip={_nullable(provider.zip)}"
        f" fips={_nullable(provider.fips_county_code)}"
        f" phone={_nullable(provider.phone)}"
        f" ownership={_nullable(provider.ownership)}",
    ]
    services = sorted(service.name for service in provider.services_provided)
    lines.append(f"services: [{', '.join(services)}]")
    lines.append("attributes:")
    for key in sorted(provider.attributes):
        lines.append(f"  {key} = {render_value(provider.attributes[key])}")
    cells = sorted(provider.get_utilization().items())
    rendered_cells = ", ".join(f"{year}|{key}|{count}" for (year, key), count in cells)
    lines.append(f"utilization: [{rendered_cells}]")
    lines.append("clinicians:")
    for specialty in sorted(provider.clinician_map):
        lines.append(f"  {specialty}:")
        for clinician in provider.clinician_map[specialty]:
            block = dump_clinician(clinician).replace("\n", "\n    ")
            lines.append(f"    {block}")
    return "\n".join(lines)
