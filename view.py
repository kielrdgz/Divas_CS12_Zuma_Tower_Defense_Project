#pyright: strict

from __future__ import annotations

import pyxel
from enemies import Enemy
from data import Bullet, CellType, Color, Direction, EnemyStatus, GameState, PYXEL_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE
    
BULLET_RADIUS = 5
ENEMY_HALF = CELL_SIZE // 2

COL_WHITE = 7
COL_DARK = 1
COL_YELLOW = 10
COL_ORANGE = 9
COL_GREEN = 11
COL_RED = 8
COL_GRAY = 13
COL_BLUE = 5

class ZumaTowerView:
    def start_game(self, update_fn: object, draw_dn: object) -> None:
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Zuma Tower Defense", fps=FPS)
        pyxel.mouse(True)
        pyxel.run(
            getattr(update_fn, "update"),
            getattr(draw_dn, "draw")
        )

    def reset_screen(self):
        pyxel.cls(0)

    def draw_paths(self, paths: list[list[tuple[float, float]]]) -> None:
        for path in paths:
            for i in range(len(path) - 1):
                x1, y1 = path[i]  # start point of segment
                x2, y2 = path[i+1]  # end point of segment
                
                pyxel.line(x1, y1, x2, y2, COL_BLUE)  # draw straight line between points
            
    def draw_enemies(self, enemies: list[Enemy]) -> None:
        for enemy in enemies:
            if enemy.status != EnemyStatus.ALIVE:
                continue
            if enemy.x < -CELL_SIZE:
                continue
            col = PYXEL_COLOR[enemy.color]
            ex = int(enemy.x)
            ey = int(enemy.y)
            pyxel.rect(ex - ENEMY_HALF, ey - ENEMY_HALF,
                       ENEMY_HALF * 2, ENEMY_HALF * 2, col)  # filled
            pyxel.rectb(ex - ENEMY_HALF, ey - ENEMY_HALF,
                        ENEMY_HALF * 2, ENEMY_HALF * 2, COL_DARK)  # outline
 
    def draw_bullets(self, bullets: list[Bullet]) -> None:
        for bullet in bullets:
            col = PYXEL_COLOR[bullet.color]
            pyxel.circ(int(bullet.x), int(bullet.y), BULLET_RADIUS, col)
 
    def draw_shooter(self, shooter_x: float, shooter_y: float, bullet_color: Color) -> None:
        sx = int(shooter_x)
        sy = int(shooter_y)
        pyxel.tri(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_WHITE)  # white triangle filled
        pyxel.trib(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_DARK)  # outline
        col = PYXEL_COLOR[bullet_color]
        pyxel.circ(sx, sy, 3, col)  # shows next bullet color

    def draw_towers(self, rows: int, cols: int, grid: list[list[CellType]]) -> None:
        for r in range(rows):  # scans grid for towers
            for c in range(cols):
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                if grid[r][c] == CellType.TOWER:              # can still change colors of towers since medyo similar with bullets
                    pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, 9) # orange block for normal tower
                elif grid[r][c] == CellType.UPGRADED_TOWER:
                    pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, 2) # purple block for upgraded tower
 
    def draw_hud(self, user_hp: int, total_exp: int, curr_round: int, max_rounds: int, state: GameState, pending_direction: Direction) -> None:
        pyxel.text(4, 4,  f"HP:  {user_hp}", COL_WHITE)
        pyxel.text(4, 12, f"EXP: {total_exp}", COL_WHITE)
        pyxel.text(4, 20, f"Round: {curr_round}/{max_rounds}", COL_WHITE)
        
        if state == GameState.ROUND_PENDING: # screen that shows in between rounds
            pyxel.rect(40, 90, 240, 80, COL_DARK)
            pyxel.text(50, 98, "ROUND 1 COMPLETE!", COL_WHITE)
            pyxel.text(50, 112, f"Current tower direction when placed (WASD): {pending_direction}", COL_YELLOW)
            pyxel.text(50, 122, "Click grid to place Tower (Cost: 5 EXP)", COL_YELLOW)
            pyxel.text(50, 132, "Click tower to upgrade (Cost: 5 EXP)", COL_ORANGE)
            pyxel.text(50, 146, "Press Q to exit.", COL_GRAY)
            pyxel.text(50, 158, "Press SPACE to start Round 2", COL_GREEN)
 
    def draw_game_over(self, total_exp: int, won: bool) -> None:
        pyxel.rect(60, 90, 200, 60, COL_DARK)
        if won:  # win message
            pyxel.text(100, 100, "YOU WIN!", COL_WHITE)
            pyxel.text(80,  112, f"EXP earned: {total_exp}", COL_WHITE)
        else:  # lose message
            pyxel.text(100, 100, "GAME OVER", COL_RED)
        pyxel.text(80, 128, "Press Q to exit.", COL_GRAY)