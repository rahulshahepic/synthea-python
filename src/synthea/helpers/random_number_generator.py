"""Java RandomNumberGenerator interface and default methods."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Protocol, overload


class RandomNumberGenerator(Protocol):
    """Java: org.mitre.synthea.helpers.RandomNumberGenerator."""

    def rand(self, *args: float | int | list[float] | list[int] | str | None) -> float | str:
        """Java: RandomNumberGenerator#rand overloads."""
        ...

    def rand_boolean(self) -> bool:
        """Java: RandomNumberGenerator#randBoolean."""
        ...

    def rand_gaussian(self) -> float:
        """Java: RandomNumberGenerator#randGaussian."""
        ...

    def rand_int(self, bound: int | None = None) -> int:
        """Java: RandomNumberGenerator#randInt overloads."""
        ...

    def rand_long(self) -> int:
        """Java: RandomNumberGenerator#randLong."""
        ...

    def rand_uuid(self) -> str:
        """Java: RandomNumberGenerator#randUUID."""
        ...

    def get_count(self) -> int:
        """Java: RandomNumberGenerator#getCount."""
        ...

    def get_seed(self) -> int:
        """Java: RandomNumberGenerator#getSeed."""
        ...


class RandomNumberGeneratorDefaults:
    """Java: RandomNumberGenerator default rand overloads (mixin)."""

    def _rand(self) -> float:
        """Java: RandomNumberGenerator#rand(), implemented by subclass."""
        raise NotImplementedError

    def rand_int(self, bound: int | None = None) -> int:
        """Java: RandomNumberGenerator#randInt(int), implemented by subclass."""
        raise NotImplementedError

    @overload
    def rand(self) -> float: ...

    @overload
    def rand(self, low: float, high: float) -> float: ...

    @overload
    def rand(self, low: float, high: float, decimals: int | None) -> float: ...

    @overload
    def rand(self, low: list[float] | list[int]) -> float: ...

    @overload
    def rand(self, low: str, *choices: str) -> str: ...

    def rand(
        self,
        low: float | list[float] | list[int] | str | None = None,
        high: float | str | None = None,
        *rest: int | str | None,
    ) -> float | str:
        """Java: RandomNumberGenerator#rand() and all interface default overloads."""
        if low is None and high is None and not rest:
            return self._rand()
        if isinstance(low, str):
            choices = (low, *([high] if isinstance(high, str) else []), *rest)
            if not all(isinstance(choice, str) for choice in choices):
                raise TypeError("choices must be strings")
            return choices[self.rand_int(len(choices))]
        if isinstance(low, list):
            if high is not None or rest:
                raise TypeError("array overload takes one argument")
            if len(low) != 2:
                raise ValueError(f"input range must be of length 2 -- got {low}")
            if low[0] > low[1]:
                raise ValueError(f"range must be of the form {{low, high}} -- got {low}")
            return float(low[0]) + (float(low[1]) - float(low[0])) * self._rand()
        if not isinstance(low, (float, int)) or not isinstance(high, (float, int)):
            raise TypeError("expected numeric low and high")
        if len(rest) > 1 or (rest and rest[0] is not None and not isinstance(rest[0], int)):
            raise TypeError("expected optional integer decimal count")
        value = float(low) + ((float(high) - float(low)) * self._rand())
        if rest and rest[0] is not None:
            decimals = rest[0]
            assert isinstance(decimals, int)
            value = float(Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP))
        return value
