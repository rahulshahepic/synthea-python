"""DefaultRandomNumberGenerator port from Synthea Java."""

from __future__ import annotations

from synthea.helpers.random_number_generator import RandomNumberGeneratorDefaults
from synthea.javacompat.random import JavaRandom
from synthea.javacompat.uuid import java_uuid


class DefaultRandomNumberGenerator(RandomNumberGeneratorDefaults):
    """Java: org.mitre.synthea.helpers.DefaultRandomNumberGenerator."""

    def __init__(self, seed: int) -> None:
        """Java: DefaultRandomNumberGenerator#DefaultRandomNumberGenerator(long)."""
        self.seed = seed
        self.random = JavaRandom(seed)
        self.count = 0

    def get_seed(self) -> int:
        """Java: DefaultRandomNumberGenerator#getSeed."""
        return self.seed

    def _rand(self) -> float:
        """Java: DefaultRandomNumberGenerator#rand."""
        self.count += 1
        return self.random.next_double()

    def rand_boolean(self) -> bool:
        """Java: DefaultRandomNumberGenerator#randBoolean."""
        self.count += 1
        return self.random.next_boolean()

    def rand_gaussian(self) -> float:
        """Java: DefaultRandomNumberGenerator#randGaussian."""
        self.count += 1
        return self.random.next_gaussian()

    def rand_int(self, bound: int | None = None) -> int:
        """Java: DefaultRandomNumberGenerator#randInt() and #randInt(int)."""
        self.count += 1
        return self.random.next_int(bound)

    def rand_long(self) -> int:
        """Java: DefaultRandomNumberGenerator#randLong."""
        self.count += 1
        return self.random.next_long()

    def rand_uuid(self) -> str:
        """Java: DefaultRandomNumberGenerator#randUUID (one counted long call)."""
        return java_uuid(self.seed, self.rand_long())

    def get_count(self) -> int:
        """Java: DefaultRandomNumberGenerator#getCount."""
        return self.count
