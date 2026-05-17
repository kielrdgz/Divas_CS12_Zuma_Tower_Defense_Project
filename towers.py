#pyright: strict

from enum import StrEnum
from abc import ABC, abstractmethod

class Tower(ABC):
    def __init__(self, cost: int, x_loc: int, y_loc: int):
        ...
        

