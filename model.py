#pyright: strict
from __future__ import annotations
from data import Color, EnemyStatus, GameState, CellType, Bullet, Direction, GameOverCondition, SCREEN_HEIGHT, SCREEN_WIDTH, CELL_SIZE, FPS, BULLET_SPEED
from enemies import Enemy
from towers import Tower, UpgradedTower
from random import Random

COLORS: list[Color] = [
    Color.RED, Color.ORANGE, Color.YELLOW,
    Color.GREEN, Color.BLUE, Color.VIOLET
    ]
ENEMY_SPEED: float = CELL_SIZE / (2 * FPS)
SPAWN_INTERVAL: int = FPS * 2 # new enemy every two secs

# simple game over condition and enemy pop up plan is not used anywhere sooo check nalang again before submitting if it's ever used, baka kailangan in the future
class SimpleGameOverCondition:
    def is_game_over(self, user_hp: int, spawned_enemies: int, killed: int, active_enemies: int) -> bool:
        if user_hp <= 0:
            return True
        if spawned_enemies > 0 and killed >= spawned_enemies and active_enemies == 0:
            return True 
        return False
    
class SimpleEnemyPopupPlan:
    def enemy_popup(self, curr_tick: int, enemies: list[Enemy], rng: Random) -> list[int]:
        if curr_tick % 30 == 0:
            li = [idx for idx, e in enumerate(enemies) if e.status == EnemyStatus.ALIVE and e.base_cooldown_ticks == 0] # not sure if tama tong base cooldown ticks
            x = len(li)
            min_enemies = 1
            if li:
                return rng.sample(li, rng.randint(min_enemies, max(1, 2 * x // 3)))
            return li
        return []


class ZumaTowerModel:
    def __init__(self, enemies: list[Enemy], user_hp: int, max_rounds: int, game_over_condition: GameOverCondition, rng: Random, paths: list[list[tuple[float, float]]]):
        self._max_rounds: int = max_rounds
        self._curr_round: int = 1
        self._user_hp = user_hp
        self._max_hp = user_hp
        self._game_over_condition: GameOverCondition = game_over_condition # remove if di natin kailangan
        self.rng = rng
        
        # not sure if this is needed also
        self._enemies: list[Enemy] = enemies
        for i, e in enumerate(self._enemies):
            e.set_index(i)

        self._active_towers: list[Tower] = []
        self._moving_bullets: list[Bullet] = []

        self._rows: int = SCREEN_HEIGHT // CELL_SIZE
        self._cols: int = SCREEN_WIDTH // CELL_SIZE
        self._grid: list[list[CellType]] = [[CellType.EMPTY for _ in range(self._cols)] for _ in range(self._rows)]
        
        self._state: GameState = GameState.ONGOING
        self._prev_state: GameState = GameState.ONGOING # not used yet, but for pausing i think
        self._is_game_over: bool = False
        self._curr_tick: int = 0
        self._total_exp: int = 0
        
        self._tot_spawned: int = 0
        self._tot_killed: int = 0
        self._next_spawn_idx: int = 0
        
        self._shooter_x: float = SCREEN_WIDTH / 2
        self._shooter_y: float = SCREEN_HEIGHT - CELL_SIZE
        
        active_colors = list(set(e.color for e in self._enemies))
        self._bullet_color: Color = self.rng.choice(active_colors)
        
        raw_paths: list[list[tuple[float, float]]] = paths if paths else [
            [(float(SCREEN_WIDTH // 2), float(SCREEN_HEIGHT // 4)),
            (float(SCREEN_WIDTH // 2), float(SCREEN_HEIGHT - 60))]
        ] # use paths given or if none, straight lines
        self._paths: list[list[tuple[float, float]]] = [
            self._build_path(p) for p in raw_paths
        ]
        
        self._bullet_radius: int = 5
        self._enemy_half: int = CELL_SIZE // 2

        self._shoot_cooldown: int = 0
        self._frames_per_shot: int = int(FPS / 0.9)

        self._pending_direction: Direction = Direction.UP

    # properties

    @property
    def curr_round(self) -> int:
        return self._curr_round
    
    @property
    def max_rounds(self) -> int:
        return self._max_rounds
        
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
    
    # helpers

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
                if e.status != EnemyStatus.ALIVE:
                    continue
                if e.x <= -CELL_SIZE:
                    continue
                
                if bullet.color != e.color:
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
        if self._next_spawn_idx < len(self._enemies) and self._curr_tick % SPAWN_INTERVAL == 0:
            e = self._enemies[self._next_spawn_idx] # get next enemy
            path_idx = self.rng.randrange(len(self._paths))
            e.assign_path(path_idx) # randomly pick its path
            start = self._paths[path_idx][0]
            e.set_position(start[0], start[1]) # put enemy in start point
            self._next_spawn_idx += 1
            self._tot_spawned += 1

        # move enemies
        for e in self._enemies:
            if e.status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE: # move enemies that are alive and entered screen
                path = self._paths[e.path_idx]
                e.move(path, ENEMY_SPEED)
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

            vx, vy = self._direction_velocity(tower.direction) # get velocity of its direction
            active_colors = list(set(e.color for e in self._enemies if e.status == EnemyStatus.ALIVE))
            if not active_colors:
                active_colors = list(Color)

            if tower.is_upgraded: # upgraded tower shoots two bullets at same time with slightly offset pos so that it's still seen
                color1, color2 = self.rng.sample(active_colors, min(2, len(active_colors))) # pick 2 dif random colors
                self._moving_bullets.append(Bullet(tower.x, tower.y, vx, vy, color1))
                self._moving_bullets.append(Bullet(tower.x, tower.y + 5, vx, vy, color2))
            else: # normal tower shoots one bullet
                color = self.rng.choice(list(Color))
                self._moving_bullets.append(Bullet(tower.x, tower.y, vx, vy, color))

            tower.reset_cooldown()

        # collisions
        self._check_collisions()
        
        # end of frame state
        active_count = sum(1 for e in self._enemies if e.status == EnemyStatus.ALIVE and e.x >= -CELL_SIZE)
        
        if self._user_hp <= 0:
            self._is_game_over = True
            self._state = GameState.GAMEOVER
            
        elif self._tot_spawned >= len(self._enemies) and active_count == 0: # all anemies have been spawned and are dead
            if self._curr_round < self._max_rounds: # there's more rounds
                self._state = GameState.ROUND_PENDING 
            else: # last round
                self._is_game_over = True
                self._state = GameState.GAMEOVER    

    def start_next_round(self) -> None:
        if self._state == GameState.ROUND_PENDING: # reset
            self._curr_round += 1
            self._tot_spawned = 0
            self._next_spawn_idx = 0
            self._tot_killed = 0
            
            for e in self._enemies:
                e.set_status(EnemyStatus.ALIVE) # revive enemies for next round
                path_idx = self.rng.randrange(len(self._paths)) # assign random path
                e.assign_path(path_idx)
                start = self._paths[path_idx][0]    # off-screen start
                e.set_position(start[0], start[1])
                e.set_waypoint_idx(1)               # target the first real waypoint
                            
            self._state = GameState.ONGOING

    def try_place_tower(self, row: int, col: int) -> bool:
        if self._state != GameState.ROUND_PENDING: # only in between rounds
            return False
            
        TOWER_COST = 5
        
        if self._total_exp >= TOWER_COST and self._grid[row][col] == CellType.EMPTY: # have enough xp and empty cell
            self._total_exp -= TOWER_COST
            self._grid[row][col] = CellType.TOWER # mark cell as with tower
            
            tower_x = (col * CELL_SIZE) + (CELL_SIZE / 2)
            tower_y = (row * CELL_SIZE) + (CELL_SIZE / 2) # center of cell
            self._active_towers.append(Tower(tower_x, tower_y, self._pending_direction)) # add to list of towers
            return True
            
        return False
    
    def try_upgrade_tower(self, row: int, col: int) -> bool:
        if self._state != GameState.ROUND_PENDING: # only in between rounds
            return False

        if self._grid[row][col] != CellType.TOWER: # there's a normal tower in the cell clicked
            return False

        tower_x = (col * CELL_SIZE) + (CELL_SIZE / 2)
        tower_y = (row * CELL_SIZE) + (CELL_SIZE / 2)

        for i, tower in enumerate(self._active_towers):
            if tower.x == tower_x and tower.y == tower_y:
                if tower.is_upgraded:
                    return False
                if self._total_exp < UpgradedTower.UPGRADE_COST:
                    return False
                self._total_exp -= UpgradedTower.UPGRADE_COST
                self._active_towers[i] = UpgradedTower(tower_x, tower_y, tower.direction) # replace tower with upgraded tower with same dir
                self._grid[row][col] = CellType.UPGRADED_TOWER  # new cell type
                return True

        return False
    
    def shoot(self, target_x: float, target_y: float) -> None:
        if self._state != GameState.ONGOING:
            return
            
        if self._shoot_cooldown > 0:  # still on cooldown
            return 
        
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
            
            active_colors = list(set(e.color for e in self._enemies))
            if active_colors:
                new_color = self.rng.choice(active_colors)
            else:
                new_color = color 
                
            self._bullet_color = new_color  # next color
            
            bullet = Bullet(origin_x, origin_y, vx, vy, color)
            self._moving_bullets.append(bullet) # create bullet and add to list
            
            self._shoot_cooldown = self._frames_per_shot # start cooldown so spamming not allowed
        
    def set_pending_direction(self, direction: Direction) -> None:
        self._pending_direction = direction # to set direction of next tower



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


    
    
    
    

    # i think no need na to
    # @classmethod
    # def get_phase1_model(cls) -> ZumaTowerModel:
    #     rng = Random()
    #     enemies: list[Enemy] = [
    #         NormalEnemy.standard(Color.RED) for _ in range(5)
    #     ]
    #     return cls(
    #         enemies=enemies,
    #         user_hp=2,
    #         max_rounds=1,
    #         game_over_condition=SimpleGameOverCondition(),
    #         rng=rng,
    #     )