"""SimpleYML tests, mirroring the SimpleYML javadoc example and the
SnakeYAML scalar typing the parity probe records.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from synthea.helpers.simple_yml import SimpleYML

DOC = "foo:\n  bar: 2\n  baz: 4\n  qux:\n    corge: 9\n    grault: -1\nplugh: 7\n"


def test_get_paths() -> None:
    """Java: SimpleYML#get examples from the class javadoc."""
    doc = SimpleYML(DOC)
    assert doc.get("foo.bar") == 2
    assert doc.get("foo.baz") == 4
    assert doc.get("foo.qux.corge") == 9
    assert doc.get("foo.qux.grault") == -1
    assert doc.get("plugh") == 7
    assert doc.get("foo") == {"bar": 2, "baz": 4, "qux": {"corge": 9, "grault": -1}}
    assert doc.internal_map is not None
    assert doc.internal_map["plugh"] == 7


def test_get_missing_leaf_is_none() -> None:
    """Java: Map.get of an absent key returns null."""
    doc = SimpleYML(DOC)
    assert doc.get("missing") is None
    assert doc.get("foo.missing") is None


def test_get_through_missing_or_scalar() -> None:
    """Java: walking through null is an NPE; through a scalar, a ClassCast."""
    doc = SimpleYML(DOC)
    with pytest.raises(AttributeError):
        doc.get("missing.deep")
    with pytest.raises(AttributeError):
        doc.get("foo.missing.deep")
    with pytest.raises(TypeError):
        doc.get("foo.bar.deep")
    with pytest.raises(AttributeError):
        SimpleYML("").get("x")


def test_non_map_document_fails_construction() -> None:
    """Java: the constructor's cast to Map throws ClassCastException."""
    with pytest.raises(TypeError):
        SimpleYML("- a\n- b\n")
    with pytest.raises(TypeError):
        SimpleYML("just a scalar\n")
    assert SimpleYML("").internal_map is None


def test_scalar_typing() -> None:
    """SnakeYAML (YAML 1.1) scalar resolution, as ported."""
    doc = SimpleYML(
        "i: 42\nbig: 3000000000\nf: 1.5\nexp: 1.0e3\nexp2: 1e3\n"
        "t: true\ny: yes\noffv: off\nn: null\ntilde: ~\ns: hello\n"
        "oct: 012\nhex: 0x1F\nbin: 0b101\nzero_o: 0o17\nsex: 1:20\n"
        "lst: [1.0, 2.0]\ndate: 2026-01-15\n"
    )
    assert doc.get("i") == 42
    assert doc.get("big") == 3000000000
    assert doc.get("f") == 1.5
    assert doc.get("exp") == 1000.0
    assert doc.get("exp2") == 1000.0
    assert doc.get("t") is True
    assert doc.get("y") is True
    assert doc.get("offv") is False
    assert doc.get("n") is None
    assert doc.get("tilde") is None
    assert doc.get("s") == "hello"
    assert doc.get("oct") == 10
    assert doc.get("hex") == 31
    assert doc.get("bin") == 5
    assert doc.get("zero_o") == "0o17"  # SnakeYAML does not know 0o either
    assert doc.get("sex") == 80
    assert doc.get("lst") == [1.0, 2.0]
    # SnakeYAML loads timestamps as java.util.Date instants (UTC here).
    assert doc.get("date") == datetime(2026, 1, 15, tzinfo=UTC)
