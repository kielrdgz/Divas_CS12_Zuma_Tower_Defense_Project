#pyright: strict

from __future__ import annotations
from enum import StrEnum
from typing import Protocol
from random import Random

SCREEN_WIDTH: int = 320
SCREEN_HEIGHT: int = 240
FPS: int = 30
CELL_SIZE: int = 16

_DIAGONAL: float = (SCREEN_WIDTH**2 + SCREEN_HEIGHT**2) ** 0.5
BULLET_SPEED: float = _DIAGONAL / (4 * FPS) # change the 4 to make bullet speed faster/slower

class GameMode(StrEnum):
    CAMPAIGN = "CAMPAIGN"
    ENDLESS = "ENDLESS"

class GameState(StrEnum):
    MENU = "MENU"
    PAUSED = "PAUSED"
    ROUND_PENDING = "ROUNDPENDING"
    ONGOING = "ONGOING"
    QUIT = "QUIT"
    QUIT_CONFIRM = "QUIT_CONFIRM"
    GAMEOVER = "GAMEOVER"
    CAMPAIGN_SELECT = "CAMPAIGN"
    ENDLESS_SELECT = "ENDLESS"
    LEADERBOARD = "LEADERBOARD"
    CONFIRM_RESET = "CONFIRM_RESET"
    CONFIRM_MENU = "CONFIRM_MENU"
    NAME_INPUT = "NAME_INPUT"
    NAME_INPUT_DONE = "NAME_INPUT_DONE"
    SETTINGS = "SETTINGS"
    SHOP = "SHOP"
    INVENTORY = "INVENTORY"
    MAIN_MENU_SHOP = "MAIN_MENU_SHOP"
    
class CellType(StrEnum):
    EMPTY = "EMPTY"
    PATH = "PATH"
    USER = "USER" # shooter
    TUNNEL = "TUNNEL"
    TOWER = "TOWER"
    UPGRADED_TOWER = "UPGRADEDTOWER"
    
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
    PENDING = "PENDING"
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
        self._from_shooter: bool = False  # for powerup, mega bullet
        
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
    
    @property
    def from_shooter(self) -> bool:
        return self._from_shooter

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

class PowerupType(StrEnum):
    MEGA_BULLET  = "MEGA_BULLET"
    STAR         = "STAR"
    TOWER_FRENZY = "TOWER_FRENZY"

POWERUP_COST: dict[PowerupType, int] = {
    PowerupType.MEGA_BULLET:  10,
    PowerupType.STAR:         15,
    PowerupType.TOWER_FRENZY: 20,
}

POWERUP_LABEL: dict[PowerupType, str] = {
    PowerupType.MEGA_BULLET:  "Mega Bullet",
    PowerupType.STAR:         "Star",
    PowerupType.TOWER_FRENZY: "Tower Frenzy",
}

COINS_PER_ROUND: int = 10


# remove this if will not use

# if gagamitin lagay to sa taas
# if TYPE_CHECKING:
#     from enemies import Enemy

class PopupPlan(Protocol):
    def enemy_popup(self, curr_tick: int, enemies: list[Enemy], rng: Random) -> list[int]:
        ...

class GameOverCondition(Protocol):
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        ...

class SimpleGameOverCondition:
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        if user_hp <= 0:
            return True
        if spawned_enemies > 0 and killed >= spawned_enemies and active_enemies == 0:
            return True 
        return False
    
class SimpleEnemyPopupPlan:
    def __init__(self, interval: int = FPS * 2) -> None:
        self._interval: int = interval
        self._next_spawn_idx: int = 0
        self._tot_spawned: int = 0
 
    def reset(self) -> None:
        self._next_spawn_idx = 0
        self._tot_spawned = 0
 
    @property
    def tot_spawned(self) -> int:
        return self._tot_spawned
 
    def enemy_popup(
        self, curr_tick: int, enemies: list[Enemy], paths: list[list[tuple[float, float]]], rng: Random) -> list[tuple[int, int]]:
        if self._next_spawn_idx >= len(enemies):
            return []
        if curr_tick % self._interval != 0:
            return []
 
        path_idx = rng.randrange(len(paths))
        idx = self._next_spawn_idx
        self._next_spawn_idx += 1
        self._tot_spawned += 1
        return [(idx, path_idx)]