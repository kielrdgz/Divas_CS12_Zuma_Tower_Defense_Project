#pyright: strict
from __future__ import annotations
import json
import os
from random import Random
from typing import Any

from data import *
from enemies import *
from towers import *

COLORS: list[Color] = [
    Color.RED, Color.ORANGE, Color.YELLOW,
    Color.GREEN, Color.BLUE, Color.VIOLET
    ]

ENEMY_SPEED: float = (CELL_SIZE / (2 * FPS)) * 3.0 # change the 3.0 to make enemy speed faster/slower
SPAWN_INTERVAL: int = FPS * 2 # new enemy every two secs

class ZumaTowerModel:
    def __init__(self, enemies: list[Enemy], user_hp: int, max_rounds: int, game_over_condition: GameOverCondition, popupplan: PopupPlan, rng: Random, paths: list[list[tuple[float, float]]], tunnels: list[tuple[float, float, float, float]] = []):        
        self._max_rounds: int = max_rounds
        self._curr_round: int = 0
        self._user_hp = user_hp
        self._max_hp = user_hp
        self._game_over_condition: GameOverCondition = game_over_condition # remove if di natin kailangan
        self._enemy_popup: PopupPlan = popupplan
        self.rng = rng
        
        self._active_towers: list[Tower] = []
        self._tower_directions: dict[tuple[int, int], Direction] = {}
        self._moving_bullets: list[Bullet] = []

        self._rows: int = SCREEN_HEIGHT // CELL_SIZE
        self._cols: int = SCREEN_WIDTH // CELL_SIZE
        self._grid: list[list[CellType]] = [[CellType.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
        
        self._state: GameState = GameState.MENU
        self._prev_state: GameState = GameState.MENU # not used yet, but for pausing i think
        self._is_game_over: bool = False
        self._curr_tick: int = 0
        self._total_exp: int = 0
        self._game_mode: GameMode = GameMode.CAMPAIGN
        
        self._enemies: list[Enemy] = enemies
        for i, e in enumerate(self._enemies):
            e.set_index(i)
        
        self._tot_spawned: int = 0
        self._tot_killed: int = 0
        self._next_spawn_idx: int = 0
        
        self._shooter_x: float = SCREEN_WIDTH / 2
        self._shooter_y: float = SCREEN_HEIGHT - CELL_SIZE
        
        raw_paths: list[list[tuple[float, float]]] = paths if paths else [
            [(float(SCREEN_WIDTH // 2), float(SCREEN_HEIGHT // 4)),
            (float(SCREEN_WIDTH // 2), float(SCREEN_HEIGHT - 60))]
        ] # use paths given or if none, straight lines
        self._paths: list[list[tuple[float, float]]] = [
            self._build_path(p) for p in raw_paths
        ]
        self._tunnels: Any = tunnels
        
        self._bullet_radius: int = 5
        self._enemy_half: int = CELL_SIZE // 2
        self._bullet_color: Color = Color.RED

        self._shoot_cooldown: int = 0
        self._frames_per_shot: int = 5 # int(FPS / 0.9)
        self._nickname: str = ""
        self._leaderboard_file: str = "leaderboard.json"
        self._pending_direction: Direction = Direction.UP

        self._mark_path_cells()
        self._load_generation_round()

    # properties

    @property
    def curr_round(self) -> int:
        return self._curr_round
    
    @property
    def max_rounds(self) -> int:
        return self._max_rounds
        
    @property
    def tunnels(self) -> list[tuple[float, float, float, float]]:
        return self._tunnels
    
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
        return [e for e in self._enemies if e.status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE]
    
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
    def bullet_color(self) -> Color:
        return self._bullet_color
    
    @property
    def tot_killed(self) -> int:
        return self._tot_killed
    
    @property
    def tot_spawned(self) -> int:
        return self._tot_spawned
    
    @property
    def num_enemies(self) -> int:
        return len(self._enemies)
    
    @property
    def paths(self) -> list[list[tuple[float, float]]]:
        return self._paths
    
    @property
    def rows(self):
        return self._rows
    
    @property
    def cols(self):
        return self._cols
    
    @property
    def grid(self):
        return self._grid
    
    @property
    def pending_direction(self) -> Direction:
        return self._pending_direction
    
    @property
    def game_mode(self) -> GameMode:
        return self._game_mode
    
    @property
    def leaderboard_records(self) -> list[dict[str, Any]]:
        return self.load_raw_leaderboard()
    
    @property
    def confirm_prev_state(self) -> GameState:
        return self._confirm_prev_state
    
    # helpers
    
    def open_confirm_reset(self) -> None:
        self._confirm_prev_state = self._state
        self._state = GameState.CONFIRM_RESET
        
    def open_confirm_menu(self) -> None:
        self._confirm_prev_state = self._state
        self._state = GameState.CONFIRM_MENU
        
    def cancel_confirm(self) -> None:
        self._state = self._confirm_prev_state

    def set_state(self, state: GameState) -> None:
        if self._state != GameState.PAUSED and state == GameState.PAUSED:
            self._prev_state = self._state
        self._state = state

    def resume(self) -> None:
        if self._state == GameState.PAUSED:
            self._state = self._prev_state

    def resume_from_quit_confirm(self) -> None:
        self._state = self._prev_state

    def reset_game(self) -> None:
        self._curr_round = 0
        self._total_exp = 0
        self._user_hp = self._max_hp
        self._is_game_over = False  
        self._active_towers.clear()
        self._moving_bullets.clear()
        self._grid = [[CellType.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
        self._mark_path_cells()
        self._load_generation_round()

    def set_game_mode(self, mode: GameMode) -> None:
        self._game_mode = mode
        self.reset_game()

    def _load_generation_round(self) -> None:
        # self._tot_spawned = 0
        # self._next_spawn_idx = 0

        self._tot_killed = 0
        self._moving_bullets = []
        self._enemy_popup.reset()
        self._curr_tick = 0

        r = self._curr_round
        avail_colors = [ Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.BLUE, Color.VIOLET ]

        if self._game_mode == GameMode.CAMPAIGN:
            enemies = 6 + (r * 2)
            hp = 1 + (r // 4)
            regen_chance = min(0.0 + (r - 4) * 0.06, 0.4) if r > 4 else 0.0
            chm_chance = min(0.0 + (r - 2) * 0.05, 0.3) if r > 2 else 0.0
        else:
            enemies = 8 + (r * 3)
            hp = 1 + (r // 2)
            speed = 1.0 + r * 0.7
            regen_chance = min(0.0 + (r - 2) * 0.08, 0.55) if r > 2 else 0.0
            chm_chance = min(0.0 + r* 0.06, 0.4)
        
        chm_interval = max(20, 90 - r * 4)
        regen_cells = max(1, 5 - r // 2)

        self._enemies = []
        
        for idx in range(enemies):
            color = self.rng.choice(avail_colors)
            rand = self.rng.random()
            if r > 4 and rand < 0.35:
                enemy = RegeneratorEnemy(hp=hp + 1, exp=3, color=color, regen_every_cells=regen_cells)
            elif r > 2 and rand < 0.30:
                enemy = ChameleonEnemy(hp=hp, exp=2, color=color, change_interval=chm_interval)
            else:
                enemy = NormalEnemy(hp=hp, exp=1, color=color)
            enemy.set_index(idx)
            self._enemies.append(enemy)
        
        if self._enemies:
            self._bullet_color = self.rng.choice([e.color for e in self._enemies])


    # build each path with an off screen start and end point 
    def _build_path(self, waypoints: list[tuple[float, float]]) -> list[tuple[float, float]]:
        if not waypoints:
            return []
        start = (-float(CELL_SIZE), waypoints[0][1])
        end = (float(SCREEN_WIDTH + CELL_SIZE), waypoints[-1][1])
        return [start, *waypoints, end]

    # convert direction to its velocity equivalent
    def _direction_velocity(self, direction: Direction) -> tuple[float, float]:
        if direction == Direction.UP:
            return (0.0, -BULLET_SPEED)
        elif direction == Direction.DOWN:
            return (0.0, BULLET_SPEED)
        elif direction == Direction.LEFT:
            return (-BULLET_SPEED, 0.0)
        else:  # right
            return (BULLET_SPEED, 0.0)
        
    # tests bullet against alive enemy
    def _check_collisions(self) -> None:
        bullets_to_remove: set[int] = set()
        for bi, bullet in enumerate(self._moving_bullets):
            for e in self._enemies:
                if e.status != EnemyStatus.ALIVE or e.x <= -20.0:
                    continue
                if e.x <= -CELL_SIZE:
                    continue
                if bullet.color != e.color:
                    continue

                in_tunnel = False
                
                path_tunnels = self._tunnels.get(e.path_idx, [])  # pyright: ignore
                for tx, ty, tw, th in path_tunnels: # pyright: ignore
                    if tx <= e.x <= tx + tw and ty <= e.y <= ty + th:
                        in_tunnel = True
                        break
        
                if in_tunnel:
                    continue 
                
                if (abs(bullet.x - e.x) < self._enemy_half and abs(bullet.y - e.y) < self._enemy_half):
                    e.set_status(EnemyStatus.DEAD) # kill enemy
                    self._tot_killed += 1          # increment kill count
                    self._total_exp += e.exp_pts   # award exp points
                    bullets_to_remove.add(bi)      # mark bullet for removal
                    break # stop checking other enemies for this bullet

        self._moving_bullets = [
            b for i, b in enumerate(self._moving_bullets)
            if i not in bullets_to_remove
        ] # bullet list without the bullets that hit an enemy
        
    # functions
    
    def update(self) -> None:
        if self._state != GameState.ONGOING:
            return

        self._curr_tick += 1
        
        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        # spawn enemies
        # if self._next_spawn_idx < len(self._enemies) and self._curr_tick % SPAWN_INTERVAL == 0:
        #     e = self._enemies[self._next_spawn_idx]
        #     e.set_status(EnemyStatus.ALIVE) 
        #     path_idx = self.rng.randrange(len(self._paths))
        #     e.assign_path(path_idx) 
        #     start = self._paths[path_idx][0]
        #     e.set_position(start[0], start[1]) 
        #     e.set_waypoint_idx(1) 
        #     self._next_spawn_idx += 1
        #     self._tot_spawned += 1
        spawn_pairs = self._enemy_popup.enemy_popup(self._curr_tick, self._enemies, self._paths, self.rng)
        for e_idx, path_id, in spawn_pairs:
            e = self._enemies[e_idx]
            e.set_status(EnemyStatus.ALIVE)
            e.assign_path(path_id)
            start = self._paths[path_id][0]
            e.set_position(start[0], start[1])
            e.set_waypoint_idx(1)

        # move enemies
        for e in self._enemies:
            if e.status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE: # move enemies that are alive and entered screen
                path = self._paths[e.path_idx]
                old_x, old_y = e.x, e.y
                speed = 1.0 + (self._curr_round * 0.05) if self._game_mode == GameMode.ENDLESS else 1.0
                e.move(path, ENEMY_SPEED * speed)

                if e.enemy_type == EnemyType.REG: # and self._curr_tick % 45 == 0:
                    regen_e = e  # pyright: ignore
                    dist = ((e.x - old_x)**2 + (e.y - old_y)**2)**0.5
                    regen_e._cells_walked += dist / CELL_SIZE  # pyright: ignore
                    if regen_e._cells_walked >= regen_e.regen_every_cells:  # pyright: ignore
                        regen_e._cells_walked -= regen_e.regen_every_cells  # pyright: ignore
                        if 0 < regen_e._hp < regen_e.base_hp + 2:  # pyright: ignore
                            regen_e._hp += 1  # pyright: ignore
                
                if e.enemy_type == EnemyType.CHM:
                    chm_e = e  # pyright: ignore
                    if self._curr_tick % chm_e.change_interval == 0:  # pyright: ignore
                        chm_e._color = self.rng.choice([c for c in Color if c != chm_e._color]) #pyright: ignore

                if e.waypoint_idx >= len(path): # enemy reached end of path
                    e.set_status(EnemyStatus.DEAD)
                    self._user_hp -= 1
                    
        # move bullets
        for b in self._moving_bullets:
            b.update()
        self._moving_bullets = [b for b in self._moving_bullets if b.is_moving] # remove bullets that went out of screen
        
        # towers shooting
        for tower in self._active_towers:
            tower.update_cooldown()

            if not tower.can_shoot():
                continue
            
            grid_c = int(tower.x // CELL_SIZE)
            grid_r = int(tower.y // CELL_SIZE)
            assigned_dir = self._tower_directions.get((grid_r, grid_c), tower.direction)

            vx, vy = self._direction_velocity(assigned_dir) # get velocity of tower's direction
            # active_colors = list(set(e.color for e in self._enemies if e.status == EnemyStatus.ALIVE))
            active_colors = []
            if not active_colors:
                active_colors = list(Color)
            if not any(e.status == EnemyStatus.ALIVE for e in self._enemies):
                continue
            
            if vy == 0:
                oldx, oldy = 0.0, 5.0
            else:
                oldx, oldy = 5.0, 0.0

            if tower.double_shot:
                color1 = self.rng.choice(active_colors)
                color2 = self.rng.choice(active_colors)
                self._moving_bullets.append(Bullet(tower.x - oldx, tower.y - oldy, vx, vy, color1))
                self._moving_bullets.append(Bullet(tower.x + oldx, tower.y + oldy, vx, vy, color2))
            else:
                color = self.rng.choice(active_colors)
                self._moving_bullets.append(Bullet(tower.x, tower.y, vx, vy, color))

            # if tower.is_upgraded: 
            #     sample_size = min(2, len(active_colors))
            #     chosen = self.rng.sample(active_colors, sample_size)
            #     color1 = chosen[0]
            #     color2 = chosen[1] if sample_size > 1 else chosen[0] 
            #     self._moving_bullets.append(Bullet(tower.x, tower.y, vx, vy, color1))
            #     self._moving_bullets.append(Bullet(tower.x, tower.y + 5, vx, vy, color2))
            # else: # normal tower shoots one bullet
            #     color = self.rng.choice(list(Color))
            #     self._moving_bullets.append(Bullet(tower.x, tower.y, vx, vy, color))

            tower.reset_cooldown()

        # collisions
        self._check_collisions()
        
        # end of frame state
        active_count = sum(1 for e in self._enemies if e.status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE)
        tot_spawned = self._enemy_popup.tot_spawned
        total_round_enemies = len(self._enemies)

        if self._user_hp <= 0:
            self._state = GameState.GAMEOVER
            self._is_game_over = True
            self.save_leaderboard()  # save progress automatically on death
            return None

        if tot_spawned >= total_round_enemies and active_count == 0:
            if self._game_mode == GameMode.CAMPAIGN and self._curr_round >= self._max_rounds:
                self._state = GameState.GAMEOVER
                self._is_game_over = True
                self.save_leaderboard()
            else:
                self._state = GameState.ROUND_PENDING

        if self._game_over_condition.is_game_over(self._user_hp, self._tot_spawned, self._tot_killed, active_count):
            if self._user_hp <= 0:
                self._state = GameState.GAMEOVER
                self._is_game_over = True
            elif self._tot_spawned >= len(self._enemies) and active_count == 0:
                if self._game_mode == GameMode.CAMPAIGN and self._curr_round >= self.max_rounds:
                    self._state = GameState.GAMEOVER
                    self._is_game_over = True
                else:
                    self._state = GameState.ROUND_PENDING

    def start_next_round(self) -> None:
        if self._state != GameState.ROUND_PENDING:
            return None
        self._curr_round += 1
        if self._game_mode == GameMode.CAMPAIGN:
            self._curr_round = min(self._curr_round, self._max_rounds)
        self._state = GameState.ONGOING
        self._load_generation_round()

    def start_round_one(self) -> None:
        self._curr_round = 1
        self._state = GameState.ONGOING
        self._load_generation_round()

    def try_place_tower(self, row: int, col: int) -> bool:
        if self._state != GameState.ROUND_PENDING: # only in between rounds
            return False
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        if self._grid[row][col] in (CellType.TOWER, CellType.UPGRADED_TOWER, CellType.PATH, CellType.TUNNEL):
            return False
            
        cost = Tower.COST
        
        if self._total_exp >= cost and self._grid[row][col] == CellType.EMPTY: # have enough xp and empty cell
            self._total_exp -= cost
            self._grid[row][col] = CellType.TOWER # mark cell as with tower
            
            tower_x = (col * CELL_SIZE) + (CELL_SIZE / 2)
            tower_y = (row * CELL_SIZE) + (CELL_SIZE / 2) # center of cell
            
            self._tower_directions[(row, col)] = self._pending_direction
            self._active_towers.append(Tower(tower_x, tower_y, self._pending_direction)) # add to list of towers
            return True
            
        return False
    
    def try_upgrade_tower(self, row: int, col: int) -> bool:
        if self._state != GameState.ROUND_PENDING: # only in between rounds
            return False
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        if self._grid[row][col] not in (CellType.TOWER, CellType.UPGRADED_TOWER): # there's a normal tower in the cell clicked
            print("wow")
            return False

        tower_x = (col * CELL_SIZE) + (CELL_SIZE / 2)
        tower_y = (row * CELL_SIZE) + (CELL_SIZE / 2)

        for i, tower in enumerate(self._active_towers):
            if abs(tower.x - tower_x) < 1.0 and abs(tower.y - tower_y) < 1.0:
                if tower.is_upgraded:
                    return False
                if self._total_exp < UpgradedTower._cost:
                    return False
                self._total_exp -= UpgradedTower._cost
                curr_dir: Direction = self._tower_directions.get((row, col), tower.direction)
                self._active_towers[i] = UpgradedTower(tower_x, tower_y, curr_dir) # replace tower with upgraded tower with same dir
                self._grid[row][col] = CellType.UPGRADED_TOWER  # new cell type
                return True

        return False
    
    def change_spec_tower_dir(self, row: int, col: int, direction: Direction) -> bool:
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        if self._grid[row][col] not in (CellType.TOWER, CellType.UPGRADED_TOWER):
            return False
        
        self._tower_directions[(row, col)] = direction
        tx = (col * CELL_SIZE) + (CELL_SIZE / 2)
        ty = (row * CELL_SIZE) + (CELL_SIZE / 2)
        for t in self._active_towers:
            if t.x == tx and t.y == ty:
                t.set_direction(direction)
                return True
        return False
    
    def try_remove_tower(self, row: int, col: int) -> bool:
        if self._state != GameState.ROUND_PENDING:
            return False
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        if self._grid[row][col] not in (CellType.TOWER, CellType.UPGRADED_TOWER):
            return False
        
        tx = (col * CELL_SIZE) + (CELL_SIZE / 2)
        ty = (row * CELL_SIZE) + (CELL_SIZE / 2)

        new_active = []
        exp = 0
        for t in self._active_towers:
            if not (t.x == tx and t.y == ty):
                new_active.append(t)
            else:
                exp = t.COST
        self._active_towers = new_active

        if (row, col) in self._tower_directions:
            del self._tower_directions[(row, col)]

        self._grid[row][col] = CellType.EMPTY
        self._total_exp += exp
        return True
    
    def shoot(self, target_x: float, target_y: float) -> None:
        if self._state != GameState.ONGOING or self._shoot_cooldown > 0:
            return None
        
        origin_x = self._shooter_x  # shooter's pos
        origin_y = self._shooter_y
        dx = target_x - origin_x
        dy = target_y - origin_y
        d = (dx**2 + dy**2)**0.5 # straight line distance from shooter to target
        
        if d > 0:
            speed = BULLET_SPEED
            vx = (dx / d) * speed
            vy = (dy / d) * speed # per frame velocity
            
            color = self._bullet_color
            
            # active_colors = list(set(e.color for e in self._enemies))
            active_colors = list(Color).copy()
            if active_colors:
                new_color = self.rng.choice(active_colors)
            else:
                new_color = color 
                
            self._bullet_color = new_color  # next color
            
            bullet = Bullet(origin_x, origin_y, vx, vy, color)
            self._moving_bullets.append(bullet) # create bullet and add to list
            
            # alive_enem = [e for e in self._enemies if e.status == EnemyStatus.ALIVE]
            # if alive_enem:
            #     chosen = self.rng.choice(alive_enem)
            #     if chosen.enemy_type == EnemyType.CHM and self.rng.random() < 0.15:
            #         colors = [ Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.BLUE, Color.VIOLET]
            #         chosen.color = self.rng.choice(colors)
            #     self._bullet_color = chosen.color

            self._shoot_cooldown = self._frames_per_shot # start cooldown so spamming not allowed
        
    def set_pending_direction(self, dir: Direction) -> None:
        self._pending_direction = dir # to set direction of next tower

    def set_all_towers_direction(self, direction: Direction) -> None:
        self._pending_direction = direction
        for tower in self._active_towers:
            tower.set_direction(direction)
        for key in self._tower_directions:
            self._tower_directions[key] = direction

    def save_leaderboard(self) -> None:
        if not self._nickname.strip():
            self._nickname = "ANON"
        
        data = {
            "name": self._nickname.strip().upper(),
            "score": self._total_exp,
            "round": self._curr_round,
            "mode": self._game_mode.name
        }
        records: list[dict[str, Any]] = []

        if os.path.exists(self._leaderboard_file):
            try:
                with open(self._leaderboard_file, "r") as f:
                    records = json.load(f)
            except Exception:
                records = []
        
        records.append(data)
        records = sorted(records, key=lambda x: int(x["score"]), reverse=True)

        with open(self._leaderboard_file, "w") as f:
            json.dump(records, f, indent=4)

    def load_raw_leaderboard(self) -> list[dict[str, Any]]:
        if not os.path.exists(self._leaderboard_file):
            return []
        try:
            with open(self._leaderboard_file, "r") as f:
                return json.load(f)
        except Exception:
            return []
        
    @property
    def tower_levels(self) -> dict[tuple[int, int], int]:
        result = {}
        for r in range(self._rows):
            for c in range(self._cols):
                if self._grid[r][c] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                    tx = (c * CELL_SIZE) + (CELL_SIZE / 2)
                    ty = (r * CELL_SIZE) + (CELL_SIZE / 2)
                    for t in self._active_towers:
                        if t.x == tx and t.y == ty:
                            if isinstance(t, UpgradedTower2):
                                result[(r, c)] = 2
                            elif isinstance(t, UpgradedTower):
                                result[(r, c)] = 1
                            else:
                                result[(r, c)] = 0
        return result
    
    def _mark_path_cells(self) -> None:
        for path in self._paths:
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                
                steps = max(abs(int(x2) - int(x1)), abs(int(y2) - int(y1))) // CELL_SIZE + 1
                for s in range(steps + 1):
                    t = s / steps if steps > 0 else 0
                    ix = x1 + (x2 - x1) * t
                    iy = y1 + (y2 - y1) * t
                    col = int(ix // CELL_SIZE)
                    row = int(iy // CELL_SIZE)
                    if 0 <= row < self._rows and 0 <= col < self._cols:
                        self._grid[row][col] = CellType.PATH
                        
        tunnel_source = self._tunnels.values() if isinstance(self._tunnels, dict) else [self._tunnels]
        for tunnel_list in tunnel_source:
            if not isinstance(tunnel_list, list):
                continue
            for tx, ty, tw, th in tunnel_list:
                c0 = int(tx // CELL_SIZE)
                r0 = int(ty // CELL_SIZE)
                c1 = int((tx + tw) // CELL_SIZE)
                r1 = int((ty + th) // CELL_SIZE)
                for r in range(r0, r1 + 1):
                    for c in range(c0, c1 + 1):
                        if 0 <= r < self._rows and 0 <= c < self._cols:
                            self._grid[r][c] = CellType.TUNNEL
        
    def reset_entire_model(self) -> None:
        self._curr_round = 0
        self._total_exp = 0
        self._user_hp = self._max_hp
        self._active_towers.clear()
        self._moving_bullets.clear()
        self._grid = [[CellType.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
        self._mark_path_cells()
        self._state = GameState.MENU
        self._nickname = "ANON"
        self._is_game_over = False
        self._load_generation_round()
