#pyright: strict

from enum import StrEnum
from typing import Protocol

class ZumaTowerState(StrEnum):
    MENU = "MENU"
    PAUSE = "PAUSE"
    ROUND_PENDING = "ROUNDPENDING"
    ONGOING = "ONGOING"
    QUIT = "QUIT"
    GAMEOVER = "GAMEOVER"

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



    

