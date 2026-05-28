#pyright: strict
from __future__ import annotations
from data import (
    Color, EnemyStatus, EnemyType, GameState, CellType, Bullet, PopupPlan,
    GameOverCondition, SCREEN_HEIGHT, SCREEN_WIDTH, CELL_SIZE, FPS, BULLET_SPEED,
)
from enemies import Enemy, NormalEnemy, ChameleonEnemy
from towers import Tower
from random import Random

from data import *
from enemies import *
from towers import *

COLORS: list[Color] = [
    Color.RED, Color.ORANGE, Color.YELLOW,
    Color.GREEN, Color.BLUE, Color.VIOLET
    ]

PHASE1_COLORS: list[Color] = [Color.RED]
ENEMY_SPEED: float = CELL_SIZE / (2 * FPS)
SPAWN_INTERVAL: int = FPS * 2

# --- GAMEOVER CONDITION ---

class SimpleGameOverCondition:
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        if user_hp <= 0:
            return True # died/gameover
        if spawned_enemies > 0 and killed >= spawned_enemies and active_enemies == 0:
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
    
# --- MODEL ---

class ZumaTowerModel:
    SCREEN_WIDTH = SCREEN_WIDTH
    SCREEN_HEIGHT = SCREEN_HEIGHT
    
    def __init__(self, enemies: list[Enemy], user_hp: int, max_rounds: int, game_over_condition: GameOverCondition, rng: Random):
        self._max_rounds = max_rounds
        self._curr_round = 1
        self._user_hp = user_hp
        self._max_hp = user_hp
        self._game_over_condition = game_over_condition
        self.rng = rng
        
        self._enemies: list[Enemy] = enemies
        for i, e in enumerate(self._enemies):
            e.set_index(i)

        self._active_towers: list[Tower] = []
        self._moving_bullets: list[Bullet] = []

        self._rows: int = SCREEN_HEIGHT // CELL_SIZE
        self._cols: int = SCREEN_WIDTH // CELL_SIZE
        self._grid: list[list[CellType]] = [[CellType.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
        
        self._state: GameState = GameState.ONGOING
        self._prev_state: GameState = GameState.ONGOING
        self._is_game_over: bool = False
        self._curr_tick: int = 0
        self._total_exp: int = 0
        
        self._tot_spawned: int = 0
        self._tot_killed: int = 0
        self._next_spawn_idx: int = 0
        
        self._shooter_x: float = SCREEN_WIDTH / 2
        self._shooter_y: float = SCREEN_HEIGHT - CELL_SIZE
        
        self._bullet_color: Color = PHASE1_COLORS[0]
        
        path_y = SCREEN_HEIGHT // 2
        self._path_y: int = path_y
        self._path: list[tuple[float, float]] = [
            (float(x), float(path_y))
            for x in range(0, SCREEN_WIDTH + CELL_SIZE, CELL_SIZE)
        ]
        
        self._bullet_radius: int = 5
        self._enemy_half: int = CELL_SIZE // 2
        
    @property
    def state(self) -> GameState:
        return self._state

    @property
    def is_game_over(self) -> bool:
        return self._is_game_over
    
    @property
    def is_player_dead(self) -> bool:
        return self._user_hp <= 0
    
    @property
    def player_won(self) -> bool:
        return (
            self._tot_spawned >= len(self._enemies)
            and self._tot_killed >= self._tot_spawned
            and self._user_hp > 0
        )
    
    @property
    def enemies(self) -> list[Enemy]:
        return self._enemies
    
    @property
    def active_enemies(self) -> list[Enemy]:
        return [e for e in self._enemies if e.states == EnemyStatus.ALIVE and e.x >= 0]
    
    @property
    def bullets(self) -> list[Bullet]:
        return self._moving_bullets
    
    @property
    def user_hp(self) -> int:
        return self._user_hp
    
    @property
    def total_exp(self) -> int:
        return self._total_exp
    
    @property
    def shooter_x(self) -> float:
        return self._shooter_x
    
    @property
    def shooter_y(self) -> float:
        return self._shooter_y
    
    @property
    def path_y(self) -> int:
        return self._path_y
    
    @property
    def bullet_color(self) -> Color:
        return self._bullet_color
    
    @property
    def tot_killed(self) -> int:
        return self._tot_killed
    
    @property
    def tot_spawned(self) -> int:
        return self._tot_spawned
    
    @property
    def num_enemis(self) -> int:
        return len(self._enemies)
    
    def update(self) -> None:
        if self._state != GameState.ONGOING:
            return
        
        self._curr_tick += 1
        
        if (self._next_spawn_idx < len(self._enemies) and self._curr_tick % SPAWN_INTERVAL == 0):
            e = self._enemies[self._next_spawn_idx]
            e.set_position(-CELL_SIZE, float(self._path_y))
            self._next_spawn_idx += 1
            self._tot_spawned += 1
            
        for e in self._enemies:
            if e._status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE:
                e.move(dx=ENEMY_SPEED)
                if e.x > SCREEN_WIDTH + CELL_SIZE:
                    e._status = EnemyStatus.DEAD
                    self._user_hp -= 1
                    self._tot_killed += 1
                    
        for b in self._moving_bullets:
            b.update()
        self._moving_bullets = [b for b in self._moving_bullets if b.is_moving]
        
        self._check_collisions()
        
        active_count = sum(1 for e in self._enemies if e.status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE)
        if self._game_over_condition.is_game_over(self._user_hp, self._tot_spawned, self._tot_killed, active_count):
            self._is_game_over = True
            self._state = GameState.GAMEOVER
            
    def _check_collisions(self) -> None:
        bullets_to_remove: set[int] = set()
        for bi, bullet in enumerate(self._moving_bullets):
            for enemy in self._enemies:
                if enemy.status != EnemyStatus.ALIVE:
                    continue
                if enemy.x < -CELL_SIZE:
                    continue
                if bullet.color != enemy.color:
                    continue
                if (abs(bullet.x - enemy.x) < self._enemy_half and abs(bullet.y - enemy.y) < self._enemy_half):
                    if enemy.status == EnemyStatus.DEAD:
                        self._tot_killed += 1
                        self._total_exp += enemy._exp_pts
                    bullets_to_remove.add(bi)
                    break
        self._moving_bullets = [
            b for i, b in enumerate(self._moving_bullets)
            if i not in bullets_to_remove
        ]
        
    @classmethod
    def get_phase1_model(cls) -> ZumaTowerModel:
        rng = Random()
        enemies: list[Enemy] = [
            NormalEnemy.standard(Color.RED) for _ in range(5)
        ]
        return cls(
            enemies=enemies,
            user_hp=2,
            max_rounds=1,
            game_over_condition=SimpleGameOverCondition(),
            rng=rng,
        )
    
    # def try_place_tower(self, row: int, col: int) -> bool:
    #     if self._state != GameState.ROUNDPENDING:
    #         return False
        
    #     tower: Tower = Tower()

    #     if self._total_exp >= Tower._cost and self.is_valid_tower_place(row, col):
    #         self._total_exp -= Tower.cost
    #         self.grid[row][col] = CellType.TOWER
    #         tower._row = row
    #         tower._col = col
    #         self._active_towers.append(tower)
    #         return True
    #     return False
        
    # def is_valid_tower_place(self, row: int, col: int) -> bool:
    #     if not (0 <= row < self._rows and 0 <= col < self._cols): # out of bounds
    #         return False
    #     return self.grid[row][col] == CellType.EMPTY # cell is available/empty 
    
    # def spawn_bullet(self, target_x: float, target_y: float) -> None:
    #     global CELL_SIZE
    #     if self._state != GameState.ONGOING:
    #         return None
        
    #     origin_x = (self._user_col * CELL_SIZE) + (CELL_SIZE / 2)
    #     origin_y = (self._user_row * CELL_SIZE) + (CELL_SIZE / 2)
    #     dx = target_x - origin_x
    #     dy = target_y - origin_y
    #     d = (dx**2 + dy**2)**0.5

    #     if d > 0:
    #         speed = 6.0 
    #         vx = (dx / d) * speed
    #         vy = (dy / d) * speed
    #         color = self._color_queue.pop(0)
    #         new_color = self.rng.choice(COLORS)
    #         self._color_queue.append(new_color)
    #         bullet = Bullet(origin_x, origin_y, vy, vy, color)
    #         self._moving_bullets(bullet)

    # def pause(self) -> None:
    #     if self.state in (GameState.ONGOING, GameState.ROUND_PENDING):
    #         self._prev_state = self._state
    #         self._state = GameState.PAUSED
    #     return None

    # def resume(self) -> None:
    #     if self._state == GameState.PAUSED:
    #         self._state = self._prev_state
    #     return None
    
    # def reset(self) -> None:
    #     self._state = GameState.MENU
    #     self._user_hp = self._max_hp
    #     self._total_exp = 0
    #     self._curr_tick = 1
    #     self._curr_round = 1
    #     self._tot_spawned_enemies = 0
    #     self._tot_killed = 0
    #     self._active_towers = []
    #     self._moving_bullets = []
    #     self._color_queue = [
    #         self.rng.choice(COLORS),
    #         self.rng.choice(COLORS),
    #     ]

    #     for r in range(self._rows):
    #         for c in range(self._cols):
    #             if self._grid[r][c] == CellType.TOWER:
    #                 # only remove TOWERS, DO NOT REMOVE User and Path
    #                 self._grid[r][c] = CellType.EMPTY

    #     self._is_game_over = False

    # def check_if_game_over(self):
    #     if self._game_over_condition.is_game_over(self._user_hp, self._tot_spawned_enemies, self._tot_killed, self._active_enemies):
    #         self._is_game_over = True
    #         self._state = GameState.GAMEOVER

    # def update(self):
    #     if self._state != GameState.ONGOING:
    #         return None
        
    #     self._curr_tick += 1

    #     _ = self._popup_plan.enemy_popup(self._curr_tick, self._enemies, self.rng)

    #     for bullet in self._moving_bullets:
    #         bullet.update()

    #     self._moving_bullets = [b for b in self._moving_bullets if b.is_moving]

    #     for enemy in self._enemies:
    #         if enemy.status == EnemyStatus.ALIVE:
    #             enemy.move(1)

    #     self.check_if_game_over()

    # # configure path
    # # configure quit UI
    # # configure cancel quit


    
    
    
    
