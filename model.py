#pyright: strict

from __future__ import annotations
import random

from data import *
from enemies import *
from towers import *

# CELL_SIZE = 16

class SimpleGameOverCondition:
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        if user_hp <= 0:
            return True # died/gameover
        
        if spawned_enemies == killed and active_enemies == 0:
            return True # 
        
        return False
    
class SimpleEnemyPopupPlan:
    def enemy_popup(self, curr_tick: int, enemies: list[Enemy], rng: Random) -> list[int]:
        if curr_tick % 30 == 0:
            li = [idx for idx, e in enumerate(enemies) if e.state == EnemyState.ALIVE and m.cooldown_ticks == 0]
            x = len(li)
            min_enemies = 1
            if li:
                return rng.sample(li, rng.randint(min_enemies, max(1, 2 * x // 3)))
            return li
        return []

class ZumaTowerModel:
    def __init__(self, enemies: list[Enemy], user_hp: int, popup_plan: PopupPlan, game_over_condition: GameOverCondition, rng: Random):
        self._enemies = enemies

        for i, e in enumerate(self._enemies):
            e.set_index(i)

        self._popup_plan = popup_plan
        self._game_over_condition = game_over_condition
        self.rng: Random = rng
        self._total_exp: int = 0
        self._user_hp = user_hp
        self._is_game_over: bool = False

        self._curr_tick: int = 1

    @property
    def is_game_over(self) -> bool:
        return self._is_game_over
    
    @property
    def enemy_info(self) -> list[Enemy]:
        return self._enemies
    
    @property
    def exp(self) -> int:
        return self._total_exp
    
    