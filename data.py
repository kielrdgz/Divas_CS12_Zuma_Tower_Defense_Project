#pyright: strict

from enum import StrEnum
from typing import Protocol

SCREEN_WIDTH: int = 320
SCREEN_HEIGHT: int = 240

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

class Bullet:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Color):
        self._x = x
        self._y = y
        self._vx = vx
        self._vy = vy
        self._color = color
        self._is_moving: bool = True

    def update(self) -> None:
        self._x += self._vx 
        self._y += self._vy
        if self._x < 0 or self._x > SCREEN_WIDTH or self._y < 0 or self._y > SCREEN_HEIGHT: # out of bounds
            self._is_moving = False

class Color(StrEnum):
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    VIOLET = "VIOLET"
    # PINK = "PINK"

class Direction(StrEnum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class EnemyType(StrEnum):
    NRM = "NORMAL"
    CHM = "CHAMELEON"
    REG = "REGENERATOR"

class EnemyStatus(StrEnum):
    ALIVE = "ALIVE"
    DEAD = "DEAD" # self.hp = 0

class PopupPlan(Protocol):
    def enemy_popup(self, curr_tick: int, enemies: list[Enemy], rng: Random) -> list[int]:
        ...

class GameOverCondition(Protocol):
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        ...



    

