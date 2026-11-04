"""Locate Synthea resource files (modules, geography, providers, ...).

The Python port reads the *same* resource files as the Java reference, from
``java/src/main/resources``. Never copy resources into the Python package.
Override the location with the ``SYNTHEA_RESOURCES_DIR`` environment variable.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def resources_dir() -> Path:
    """Return the root directory that mirrors Java's classpath resources."""
    override = os.environ.get("SYNTHEA_RESOURCES_DIR")
    if override:
        return Path(override)
    return REPO_ROOT / "java" / "src" / "main" / "resources"


def resource_path(relative: str) -> Path:
    """Return the path of a resource, e.g. ``resource_path("modules/asthma.json")``."""
    return resources_dir() / relative


def read_resource(relative: str, encoding: str = "utf-8") -> str:
    """Read a text resource (Java: ``Utilities.readResource``)."""
    return resource_path(relative).read_text(encoding=encoding)
