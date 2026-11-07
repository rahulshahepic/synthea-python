"""Unit tests for ReactionProbabilities (T20).

Ports of the upstream JUnit ``ReactionProbabilitiesTest``; the assertions
mirror the Java ones. Exact sampled-severity parity is covered by the
StateProbe parity tests, not here.
"""

from __future__ import annotations

import pytest

from synthea.engine.reaction_probabilities import ReactionProbabilities, SeverityProbability
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Code, ReactionSeverity


def _cough() -> Code:
    """Java: ReactionProbabilitiesTest#setUp's cough code."""
    return Code("http://www.snomed.org/sct", "49727002", "Cough")


def _mild_none() -> ReactionProbabilities:
    """Java: ReactionProbabilitiesTest#setUp."""
    probs = [SeverityProbability("mild", 0.5), SeverityProbability("none", 0.5)]
    return ReactionProbabilities(_cough(), probs)


def test_is_populated() -> None:
    """Java: ReactionProbabilitiesTest#isPopulated."""
    assert _mild_none().is_populated() is True
    assert ReactionProbabilities(_cough(), []).is_populated() is False


def test_validate() -> None:
    """Java: ReactionProbabilitiesTest#validate."""
    assert _mild_none().validate() is True
    probs = [
        SeverityProbability("mild", 0.5),
        SeverityProbability("none", 0.5),
        SeverityProbability("severe", 0.5),
    ]
    assert ReactionProbabilities(_cough(), probs).validate() is False


def test_generate_reactions() -> None:
    """Java: ReactionProbabilitiesTest#generateReactions."""
    person = Person(0)
    severity = _mild_none().generate_severity(person)
    assert severity is None or severity == ReactionSeverity.MILD


def test_build_reaction_distributions_rejects_invalid() -> None:
    """Java: ReactionProbabilities#buildReactionDistributions throws on invalid sums."""
    probs = [SeverityProbability("mild", 0.75), SeverityProbability("none", 0.75)]
    with pytest.raises(RuntimeError, match="Invalid distribution values specified"):
        ReactionProbabilities(_cough(), probs).build_reaction_distributions()


def test_severity_probability_float32_value() -> None:
    """Java: SeverityProbability#value is a float; 0.1 widens from float32."""
    sp = SeverityProbability("mild", 0.1)
    assert sp.get_value() == 0.10000000149011612
    sp.set_value(0.5)
    assert sp.get_value() == 0.5


def test_reaction_accessors() -> None:
    """Java: ReactionProbabilities#getReaction / #setReaction."""
    rp = _mild_none()
    assert rp.get_reaction() == _cough()
    other = Code("http://www.snomed.org/sct", "233678006", "Pollen")
    rp.set_reaction(other)
    assert rp.get_reaction() == other
