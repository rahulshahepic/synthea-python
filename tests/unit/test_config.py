"""Ported from java/src/test/java/org/mitre/synthea/helpers/ConfigTest.java,
plus coverage for the typed getters and the Properties parser.

The Java tests share one static Config across the class; these do the same
module-wide, so each test loads the files it depends on explicitly.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from synthea.helpers.config import Config

TEST_RESOURCES = Path(__file__).resolve().parents[2] / "java" / "src" / "test" / "resources"


def test_config() -> None:
    """Java: ConfigTest#testConfig."""
    Config.load(TEST_RESOURCES / "test.properties")
    property_names = Config.all_property_names()
    assert property_names
    for key in ("test.foo.bar", "test.foo.baz", "test.bar", "foo"):
        assert key in property_names


def test_multi_config() -> None:
    """Java: ConfigTest#testMultiConfig — later loads override earlier ones."""
    Config.load(TEST_RESOURCES / "test.properties")
    assert Config.get("test.bar") == "42"
    Config.load(TEST_RESOURCES / "test2.properties")
    property_names = Config.all_property_names()
    assert property_names
    for key in ("test.foo.bar", "test.foo.baz", "test.bar", "foo"):
        assert key in property_names
    for key in ("test.foo.bar2", "test.foo.baz2"):
        assert key in property_names
    assert Config.get("test.bar") == "24"


def test_set_and_unset_config() -> None:
    """Java: ConfigTest#testSetAndUnsetConfig."""
    Config.load(TEST_RESOURCES / "test.properties")
    property_names = Config.all_property_names()
    assert property_names
    assert "bing.bong.do" not in property_names
    Config.set("bing.bong.do", "true")
    property_names = Config.all_property_names()
    assert property_names
    assert "bing.bong.do" in property_names
    Config.remove("bing.bong.do")
    property_names = Config.all_property_names()
    assert "bing.bong.do" not in property_names


def test_all_property_names_is_a_snapshot() -> None:
    """Java: Properties.stringPropertyNames returns a set not backed by the store."""
    snapshot = Config.all_property_names()
    Config.set("snapshot.probe", "1")
    try:
        assert "snapshot.probe" not in snapshot
    finally:
        Config.remove("snapshot.probe")


def test_typed_getters() -> None:
    """Java: Config#getAsDouble/getAsInteger/getAsLong/getAsBoolean + defaults."""
    Config.set("unit.int", "42")
    Config.set("unit.double", "2.5")
    Config.set("unit.bool", "true")
    Config.set("unit.bad", "abc")
    try:
        assert Config.get_as_integer("unit.int") == 42
        assert Config.get_as_long("unit.int") == 42
        assert Config.get_as_double("unit.int") == 42.0
        assert Config.get_as_double("unit.double") == 2.5
        assert Config.get_as_boolean("unit.bool") is True
        assert Config.get_as_boolean("unit.bad") is False
        with pytest.raises(ValueError):
            Config.get_as_integer("unit.bad")
        with pytest.raises(ValueError):
            Config.get_as_double("unit.bad")
        # Defaults apply only when the key is absent.
        assert Config.get_as_integer("unit.absent", -7) == -7
        assert Config.get_as_double("unit.absent", 9.25) == 9.25
        assert Config.get_as_boolean("unit.absent", True) is True
        with pytest.raises(ValueError):
            Config.get_as_integer("unit.bad", -7)
        # Missing key without a default: Java throws NullPointerException for
        # doubles (TypeError here) and NumberFormatException (ValueError) for
        # ints/longs, while Boolean.parseBoolean(null) is simply false.
        with pytest.raises(TypeError):
            Config.get_as_double("unit.absent")
        with pytest.raises(ValueError):
            Config.get_as_integer("unit.absent")
        with pytest.raises(ValueError):
            Config.get_as_long("unit.absent")
        assert Config.get_as_boolean("unit.absent") is False
        assert Config.get("unit.absent") is None
        assert Config.get("unit.absent", "DEF") == "DEF"
    finally:
        for key in ("unit.int", "unit.double", "unit.bool", "unit.bad"):
            Config.remove(key)


def test_properties_stream_parsing() -> None:
    """java.util.Properties semantics over the ISO-8859-1 stream overload."""
    text = (
        "# comment\n"
        "unit.a = 1\n"
        "unit.b: 2\n"
        "unit.c 3\n"
        "unit.cont = first \\\n  second\n"
        "unit.esc = a\\tb\\u0041\n"
        "unit.latin = café\n"
    )
    Config.load(io.BytesIO(text.encode("iso-8859-1")))
    try:
        assert Config.get("unit.a") == "1"
        assert Config.get("unit.b") == "2"
        assert Config.get("unit.c") == "3"
        assert Config.get("unit.cont") == "first second"
        assert Config.get("unit.esc") == "a\tbA"
        assert Config.get("unit.latin") == "café"
    finally:
        for key in ("unit.a", "unit.b", "unit.c", "unit.cont", "unit.esc", "unit.latin"):
            Config.remove(key)


def test_properties_malformed_unicode() -> None:
    """A malformed unicode escape is Java's IllegalArgumentException (ValueError)."""
    with pytest.raises(ValueError, match="Malformed"):
        Config.load(io.BytesIO(b"unit.bad = \\u00xz\n"))
    with pytest.raises(ValueError, match="Malformed"):
        Config.load(io.BytesIO(b"unit.bad = \\uu0042\n"))


def test_load_file_decodes_utf8(tmp_path: Path) -> None:
    """The File overload reads through a FileReader (UTF-8 under the parity JVM)."""
    props = tmp_path / "unit.properties"
    props.write_text("unit.file = café\n", encoding="utf-8")
    Config.load(props)
    try:
        assert Config.get("unit.file") == "café"
    finally:
        Config.remove("unit.file")
