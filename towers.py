# #pyright: strict

# from enum import StrEnum
# from abc import ABC, abstractmethod

# class Tower(ABC):
#     def __init__(self, cost: int, x_loc: int, y_loc: int):
#         ...

class Tower:
    COST: int = 5
    
    def __int__(self) -> None:
        self._row: int = 0
        self._col: int = 0