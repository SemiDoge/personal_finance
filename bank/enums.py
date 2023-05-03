from enum import Enum


class Bank(Enum):
    NULL = "NULL"
    BMO = "BMO"
    SCOTIA = "Scotiabank"
    TD = "TD Bank"

    def __str__(self):
        return self.name
