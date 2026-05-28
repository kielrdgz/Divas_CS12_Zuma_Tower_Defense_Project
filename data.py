#pyright: strict

from __future__ import annotations
from enum import StrEnum
from typing import Protocol, TYPE_CHECKING
from random import Random

if TYPE_CHECKING:
    from enemies import Enemy

SCREEN_WIDTH: int = 320
SCREEN_HEIGHT: int = 240
FPS: int = 30
CELL_SIZE: int = 16

_DIAGONAL = (SCREEN_WIDTH**2 + SCREEN_HEIGHT**2) ** 0.5
BULLET_SPEED: float = _DIAGONAL / (5 * FPS)

class GameState(StrEnum):
    MENU = "MENU"
    PAUSED = "PAUSED"
    ROUND_PENDING = "ROUNDPENDING"
    ONGOING = "ONGOING"
    QUIT = "QUIT"
    GAMEOVER = "GAMEOVER"
    STANDARD = "STANDARD"
    CAMPAIGN = "CAMPAIGN"
    ENDLESS = "ENDLESS"
    LEADERBOARD = "LEADERBOARD"

class CellType(StrEnum):
    EMPTY = "EMPTY"
    PATH = "PATH"
    USER = "USER" # shooter
    TOWER = "TOWER"
    
class Color(StrEnum):
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    VIOLET = "VIOLET"
    # PINK = "PINK"
    
PYXEL_COLOR: dict[Color, int] = {
    Color.RED: 8,
    Color.ORANGE: 9,
    Color.YELLOW: 10,
    Color.GREEN: 3,
    Color.BLUE: 12,
    Color.VIOLET: 2,
}

class EnemyType(StrEnum):
    NRM = "NORMAL"
    CHM = "CHAMELEON"
    REG = "REGENERATOR"
    
class EnemyStatus(StrEnum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"

class Bullet:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Color):
        self._x = x
        self._y = y
        self._vx = vx
        self._vy = vy
        self._color = color
        self._is_moving: bool = True
        
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
    def is_moving(self) -> bool:
        return self._is_moving

    def update(self) -> None:
        self._x += self._vx 
        self._y += self._vy
        if (self._x < 0 or self._x > SCREEN_WIDTH or self._y < 0 or self._y > SCREEN_HEIGHT): # out of bounds
            self._is_moving = False

class Direction(StrEnum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class PopupPlan(Protocol):
    def enemy_popup(self, curr_tick: int, enemies: list[Enemy], rng: Random) -> list[int]:
        ...

class GameOverCondition(Protocol):
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        ...