from enum import Enum


class Exchanges(Enum):
    OKX = "OKX"
    BINGX = "BingX"
    BITGET = "Bitget"

    def __str__(self):
        return self.value


class PnlCellStyles(Enum):
    RED = "f0bbbe"
    GREEN = "c5edc8"
    YELLOW = "ede7c5"

    def __str__(self):
        return f'<div style="background-color:#{self.value}; padding:12px; border-radius:5px; border: 1px solid black;">'
