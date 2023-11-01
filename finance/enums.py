from enum import Enum


class Bank(Enum):
    NULL = "NULL"
    BMO = "BMO"
    SCOTIA = "Scotiabank"
    TD = "TD Bank"

    def __str__(self):
        return self.name

class Quarter(Enum):
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4

    def __str__(self):
        return self.name