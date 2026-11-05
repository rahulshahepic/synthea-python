"""SimpleYML port.

Java: org.mitre.synthea.helpers.SimpleYML — SnakeYAML 1.33 ``Yaml.load``
into a ``Map<String, ?>``, with dotted-path lookup.

Scalar typing follows SnakeYAML (YAML 1.1) as closely as PyYAML allows:
a custom loader replaces PyYAML's float resolver, whose exponent must
carry an explicit sign, with SnakeYAML's (``1.0e3`` and ``1e3`` are
doubles), and converts timestamp scalars to timezone-aware UTC
``datetime`` values — SnakeYAML loads them as ``java.util.Date``
instants, where plain PyYAML would return ``date``/naive ``datetime``.
Known remaining differences are recorded in docs/porting_notes/T05.md.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML ships no type stubs

_FLOAT_RE = re.compile(
    r"^(?:[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)"
    r"(?:[eE][-+]?[0-9]+)?"
    r"|[-+]?\.(?:inf|Inf|INF)"
    r"|\.(?:nan|NaN|NAN)"
    r"|[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*)$"
)


def _construct_timestamp(loader: yaml.SafeLoader, node: yaml.Node) -> datetime:
    """SnakeYAML timestamp: a ``java.util.Date`` instant, UTC by default."""
    value = yaml.SafeLoader.construct_yaml_timestamp(loader, node)
    # A plain date becomes midnight at the start of that day, UTC.
    result = value if isinstance(value, datetime) else datetime(value.year, value.month, value.day)
    if result.tzinfo is None:
        result = result.replace(tzinfo=UTC)
    return result


class _SnakeLoader(yaml.SafeLoader):
    """SafeLoader with SnakeYAML 1.33 scalar resolution for floats/dates."""


_SnakeLoader.yaml_implicit_resolvers = {
    first: [(tag, pattern) for tag, pattern in resolvers if tag != "tag:yaml.org,2002:float"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_SnakeLoader.add_implicit_resolver("tag:yaml.org,2002:float", _FLOAT_RE, list("-+0123456789."))
_SnakeLoader.yaml_constructors = dict(yaml.SafeLoader.yaml_constructors)
_SnakeLoader.yaml_constructors["tag:yaml.org,2002:timestamp"] = _construct_timestamp


class SimpleYML:
    """Java: org.mitre.synthea.helpers.SimpleYML."""

    def __init__(self, raw_content: str) -> None:
        """Java: SimpleYML#SimpleYML.

        Java overloads:
        (String rawContent)

        Java casts the loaded document to Map; a non-map document (list or
        scalar) fails that cast in the constructor — mirrored here as
        TypeError. An empty document loads as null, as in Java.
        """
        loaded: Any = yaml.load(raw_content, Loader=_SnakeLoader)
        if loaded is not None and not isinstance(loaded, dict):
            raise TypeError(
                f"java.lang.ClassCastException: {type(loaded).__name__} "
                "cannot be cast to java.util.Map"
            )
        self.internal_map: dict[str, object] | None = loaded

    def get(self, path: str) -> object:
        """Java: SimpleYML#get.

        Java overloads:
        (String path)

        Walks maps for every segment but the last and returns the last
        segment's value (None when absent, like a Java null). Walking
        through a missing segment makes Java throw NullPointerException
        (mirrored as AttributeError); walking through a non-map value
        makes Java throw ClassCastException (mirrored as TypeError).
        """
        segments = path.split(".")
        current: object = self.internal_map
        for segment in segments[:-1]:
            nxt = self._as_map(current).get(segment)
            if nxt is not None and not isinstance(nxt, dict):
                raise TypeError(
                    f"java.lang.ClassCastException: {type(nxt).__name__} "
                    "cannot be cast to java.util.Map"
                )
            current = nxt
        return self._as_map(current).get(segments[-1])

    @staticmethod
    def _as_map(value: object) -> dict[str, object]:
        """Cast a walked value to a map, with Java's failure modes."""
        if value is None:
            raise AttributeError(
                'java.lang.NullPointerException: cannot invoke "java.util.Map.get" '
                "because the current map is null"
            )
        if not isinstance(value, dict):
            raise TypeError(
                f"java.lang.ClassCastException: {type(value).__name__} "
                "cannot be cast to java.util.Map"
            )
        return value
