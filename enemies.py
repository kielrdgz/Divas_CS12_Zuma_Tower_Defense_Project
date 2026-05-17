#pyright: strict

from enum import StrEnum
from abc import ABC, abstractmethod

class Enemy(ABC):
    def __init__(self, hp: int, exp: int, color: Color):
        ...
    
    @property
    @abstractmethod
    def base_hp(self) -> int:
        ...
    
    @property
    @abstractmethod
    def base_exp(self) -> int:
        ...

    @property
    @abstractmethod
    def base_cooldown_ticks(self) -> int:
        return 30

    # def move()

class NormalEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color):
        self._color = color
        self._hp = hp
        self._exp_pts = exp
        self._status = EnemyStatus.ALIVE
        self._type = EnemyType.NRM
        # loc
    
    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1
    
    # def move()

    @classmethod
    def standard(cls, color: Color) -> NormalEnemy:
        return cls(1, 1, color)


class ChameleonEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color):
        self._color = color
        self._hp = hp
        self._exp_pts = exp
        self._status = EnemyStatus.ALIVE
        self._type = EnemyType.CHM
        # loc
    
    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1
    
    # def move()

    @classmethod
    def standard(cls, color: Color) -> ChameleonEnemy:
        return cls(1, 1, color)
    

class RegeneratorEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color):
        self._color = color
        self._hp = hp
        self._exp_pts = exp
        self._status = EnemyStatus.ALIVE
        self._type = EnemyType.REG
        # loc
    
    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1
    
    # def move()

    @classmethod
    def standard(cls, color: Color) -> RegeneratorEnemy:
        return cls(1, 1, color)