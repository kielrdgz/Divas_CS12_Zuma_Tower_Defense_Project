#pyright: strict

from __future__ import annotations
from data import Color, EnemyStatus, EnemyType
from enemies import Enemy, NormalEnemy, ChameleonEnemy
from random import Random

from data import *
from enemies import *
from towers import *

CELL_SIZE: int = 16
SCREEN_HEIGHT: int = 240
SCREEN_WIDTH: int = 360
COLORS = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.BLUE, Color.VIOLET]

class SimpleGameOverCondition:
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        if user_hp <= 0:
            return True # died/gameover
        
        if spawned_enemies == killed and active_enemies == 0:
            return True 
        
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
    def __init__(self, enemies: list[Enemy], user_hp: int, max_rounds: int, popup_plan: PopupPlan, game_over_condition: GameOverCondition, rng: Random):
        local COLORS
        self._enemies = enemies

        for i, e in enumerate(self._enemies):
            e.set_index(i)

        self._active_towers: list[Tower] = []
        self._moving_bullets: list[Bullet] = []

        self._rows: int = 15
        self._cols: int = 20
        self._grid: list[list[CellType]] = [[CellType.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
        self._state: GameState = GameState.MENU
        self._prev_state: GameState = GameState.MENU
        self._max_rounds: int = max_rounds
        self._curr_round: int = 1
        self._user_hp = user_hp
        self._max_hp: int = user_hp
        self._popup_plan = popup_plan
        self._game_over_condition = game_over_condition
        self.rng: Random = rng
        self._total_exp: int = 0
        self._is_game_over: bool = False
        self._curr_tick: int = 1
        self._color_queue: list[Color] = [
            self.rng.choice(COLORS),
            self.rng.choice(COLORS), # show preview of next color ALWAYS
        ]

        self._user_row: int = self._rows // 2
        self._user_col: int = self._cols // 2
        self._grid[self._user_row][self._user_col] = CellType.USER

        self._tot_spawned_enemies: int = 0
        self._tot_killed: int = 0
        self._path_coords: list[tuple[int, int]] = []
        self.generate_path() # depends on GameState if GameState.STANDARD | GameState.CAMPAIGN | GameState.ENDLESS 

    def generate_path(self) -> None:
        # diko pa alam if gawa muna tayo ng maps lmao or what

    @property
    def curr_bullet_color(self) -> Color:
        return self._color_queue[0]
    
    @property
    def next_bullet_color(self) -> Color:
        return self._color_queue[1]

    @property
    def is_game_over(self) -> bool:
        return self._is_game_over
    
    @property
    def enemy_info(self) -> list[Enemy]:
        return self._enemies
    
    @property
    def exp(self) -> int:
        return self._total_exp
    
    # show timer function?

    @property
    def user_hp(self) -> int:
        return self._user_hp
    
    def try_place_tower(self, row: int, col: int) -> bool:
        if self._state != GameState.ROUNDPENDING:
            return False
        
        tower: Tower = Tower()

        if self._total_exp >= Tower._cost and self.is_valid_tower_place(row, col):
            self._total_exp -= Tower.cost
            self.grid[row][col] = CellType.TOWER
            tower._row = row
            tower._col = col
            self._active_towers.append(tower)
            return True
        return False
        
    def is_valid_tower_place(self, row: int, col: int) -> bool:
        if not (0 <= row < self._rows and 0 <= col < self._cols): # out of bounds
            return False
        return self.grid[row][col] == CellType.EMPTY # cell is available/empty 
    
    def spawn_bullet(self, target_x: floar, target_y: float) -> None:
        local CELL_SIZE
        if self._state != GameState.ONGOING:
            return None
        
        origin_x = (self._user_col * CELL_SIZE) + (CELL_SIZE / 2)
        origin_y = (self._user_row * CELL_SIZE) + (CELL_SIZE / 2)
        dx = target_x - origin_x
        dy = target_y - origin_y
        d = (dx**2 + dy**2)**0.5

        if d > 0:
            speed = 6.0 
            vx = (dx / d) * speed
            vy = (dy / d) * speed
            color = self._color_queue.pop(0)
            new_color = self.rng.choice.(COLORS)
            self._color_queue.append(new_color)
            bullet = Bullet(origin_x, origin_y, vy, vy, color)
            self._moving_bullets(bullet)

    def pause(self) -> None:
        if self.state in (GameState.ONGOING, GameState.ROUND_PENDING):
            self._prev_state = self._state
            self._state = GameState.PAUSED
        return None

    def resume(self) -> None:
        if self._state == GameState.PAUSED:
            self._state = self._prev_state
        return None
    
    def reset(self) -> None:
        self._state = GameState.MENU
        self._user_hp = self._max_hp
        self._total_exp = 0
        self._curr_tick = 1
        self._curr_round = 1
        self._tot_spawned_enemies = 0
        self._tot_killed = 0
        self._active_towers = []
        self._moving_bullets = []
        self._color_queue = [
            self.rng.choice(COLORS),
            self.rng.choice(COLORS),
        ]

        for r in range(self._rows):
            for c in range(self._cols):
                if self._grid[r][c] == CellType.TOWER:
                    # only remove TOWERS, DO NOT REMOVE User and Path
                    self._grid[r][c] = CellType.EMPTY

        self._is_game_over = False

    # configure path
    # configure quit UI
    # configure cancel quit

    def update(self) -> None:
        if self._state != GameState.ONGOING:
            return None
        
        self._curr_tick += 1

        _ = self._popup_plan.enemy_popup(self._curr_tick, self._enemies, self.rng)

        for bullet in self._moving_bullets:
            bullet.update()
        self._moving_bullets = [b for b in self._moving_bullets if b._is_moving]

        active = len([e for e in self._enemies if e._state == EnemyState.ALIVE])

        if self._game_over_condition.is_game_over(self._user_hp, self._tot_spawned_enemies, self._tot_killed, active)
            self._is_game_over = True
            self._state = GameState.GAMEOVER
        
    
    
    
    
