#pyright: strict

from __future__ import annotations
from enum import StrEnum
from abc import ABC, abstractmethod
from data import Color, EnemyType, EnemyStatus

class Enemy(ABC):
    def __init__(self, hp: int, exp: int, color: Color, enemy_type: EnemyType):
        self._color = color
        self._hp = hp
        self._exp_pts = exp
        self._status: EnemyStatus = EnemyStatus.ALIVE
        self._enemy_type = enemy_type
        self._x: float = -20.0
        self._y: float = 0.0
        self._index: int = -1
        self.waypoint_idx: int = 1

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
    def status(self) -> EnemyStatus:
        return self._status
    
    @property
    def enemy_type(self) -> EnemyType:
        return self._enemy_type
    
    @property
    def exp_points(self) -> int:
        return self._exp_pts
    
    def set_position(self, x: float, y: float) -> None:
        self._x = x
        self._y = y
 
    def set_index(self, idx: int) -> None:
        self._index = idx
 
    def hit(self) -> None:
        self._hp -= 1
        if self._hp <= 0:
            self._status = EnemyStatus.DEAD
 
    def move(self, path: list[tuple[float, float]], speed: float) -> None:
        if self.waypoint_idx >= len(path):
            return
            
        target_x, target_y = path[self.waypoint_idx]
        dx = target_x - self._x
        dy = target_y - self._y
        distance = (dx**2 + dy**2)**0.5
        
        if distance <= speed:
            self._x = target_x
            self._y = target_y
            self.waypoint_idx += 1
        else:
            self._x += (dx / distance) * speed
            self._y += (dy / distance) * speed


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