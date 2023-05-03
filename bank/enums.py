from enum import Enum


class Bank(Enum):
    BMO = "BMO"
    SCOTIA = "Scotiabank"
    TORONTO_DOMINION = "TD"

    def __str__(self):
        return self.name
