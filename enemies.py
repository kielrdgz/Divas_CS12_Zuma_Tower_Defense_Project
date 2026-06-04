#pyright: strict

from __future__ import annotations
from abc import ABC, abstractmethod
from data import Color, EnemyType, EnemyStatus, CELL_SIZE

class Enemy(ABC):
    def __init__(self, hp: int, exp: int, color: Color, enemy_type: EnemyType) -> None:
        self._hp: int = hp
        self._exp_pts: int = exp
        self._color: Color = color
        self._enemy_type: EnemyType = enemy_type
        self._status: EnemyStatus = EnemyStatus.PENDING
        self._x: float = -20.0
        self._y: float = 0.0
        self._index: int = -1  
        self._path_idx: int = 0
        self._waypoint_idx: int = 1  

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
    def x(self) -> float:
        return self._x
    
    @property
    def y(self) -> float:
        return self._y
    
    @property
    def color(self) -> Color:
        return self._color
    
    @property
    def status(self) -> EnemyStatus:
        return self._status
    
    @property
    def enemy_type(self) -> EnemyType:
        return self._enemy_type
    
    @property
    def exp_pts(self) -> int:
        return self._exp_pts
    
    @property
    def path_idx(self) -> int:
        return self._path_idx
    
    @property
    def waypoint_idx(self) -> int:
        return self._waypoint_idx
    
    def set_status(self, value: EnemyStatus) -> None:
        self._status = value
    
    def assign_path(self, path_idx: int) -> None:
        self._path_idx = path_idx
    
    def set_position(self, x: float, y: float) -> None:  # for spawning
        self._x = x
        self._y = y
 
    def set_index(self, idx: int) -> None:
        self._index = idx

    def set_waypoint_idx(self, idx: int) -> None:
        self._waypoint_idx = idx
 
    def hit(self, dmg: int) -> None:
        self._hp -= dmg
        if self._hp <= 0:
            self._status = EnemyStatus.DEAD
 
    def move(self, path: list[tuple[float, float]], speed: float) -> None:
        if self._waypoint_idx >= len(path):
            return
            
        target_x, target_y = path[self._waypoint_idx]
        dx = target_x - self._x
        dy = target_y - self._y
        distance = (dx**2 + dy**2)**0.5  
        
        if distance <= speed: 
            self._x = target_x
            self._y = target_y
            self._waypoint_idx += 1
        else:
            self._x += (dx / distance) * speed
            self._y += (dy / distance) * speed


class NormalEnemy(Enemy):
    def __init__(self, hp: int, exp: int, color: Color) -> None:
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
    def __init__(self, hp: int, exp: int, color: Color, change_interval: int = 60) -> None:
        super().__init__(hp, exp, color, EnemyType.CHM)
        self.change_interval: int = change_interval  # ticks between color changes

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
    def __init__(self, hp: int, exp: int, color: Color, regen_every_cells: int = 3) -> None:
        super().__init__(hp, exp, color, EnemyType.REG)
        self.regen_every_cells: int = regen_every_cells  # heal every n cells walked
        self._cells_walked: float = 0.0

    @property
    def base_hp(self) -> int:
        return 1

    @property
    def base_exp(self) -> int:
        return 1

    @classmethod
    def standard(cls, color: Color) -> RegeneratorEnemy:
        return cls(1, 1, color)