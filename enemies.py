#pyright: strict

from enum import StrEnum
from abc import ABC, abstractmethod

class Enemy(ABC):
    def __init__(self, hp: int, exp: int, color: Color):
        self._color = color
        self._hp = hp
        self._exp_pts = exp
        self._status = EnemyStatus.ALIVE
        self._type = type
        self._x: int = 20
        self._y: int = 20

    @property
    @abstractmethod
    def base_hp(self) -> int:
        ...

    @property
    @abstractmethod
    def base_exp(self) -> int:
        ...

    @property
    def base_cooldown_ticks(self) -> int:
        return 30
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def color(self):
        return self._color
    
    @property
    def type(self):
        return self._type

    def hit(self) -> None:
        self._hp -= 1
        if self._hp <= 0:
            self._status = EnemyStatus.DEAD

    def move(self, speed: int = 1) -> None:
        self._x += speed


class NormalEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color):
        super().__init__(hp, exp, color, EnemyType.NRM)

    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1

    @classmethod
    def standard(cls, color: Color) -> NormalEnemy:
        return cls(1, 1, color)


class ChameleonEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color):
        super().__init__(hp, exp, color, EnemyType.CHM)

    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1

    @classmethod
    def standard(cls, color: Color) -> ChameleonEnemy:
        return cls(1, 1, color)


class RegeneratorEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color):
        super().__init__(hp, exp, color,  EnemyType.REG)

    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1

    @classmethod
    def standard(cls, color: Color) -> RegeneratorEnemy:
        return cls(1, 1, color)