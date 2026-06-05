#pyright: strict

from __future__ import annotations

import pyxel
from typing import Any
from enemies import Enemy
from data import *

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
COL_PURPLE = 2

class ZumaTowerView:
    @staticmethod
    def cell_center(row: int, col: int) -> tuple[float, float]:
        """Utility helper to locate exact center positions of coordinates."""
        return (float(col * CELL_SIZE + ENEMY_HALF), float(row * CELL_SIZE + ENEMY_HALF))

    def start_game(self, update_fn: object, draw_dn: object) -> None:
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Zuma Tower Defense", fps=FPS)
        pyxel.mouse(True)

        try:
            pyxel.load("assets.pyxres")
        except Exception:
            pass
        
        try:
            pyxel.sounds[0].set("a3a2c1", "p", "7", "s", 5) 
            pyxel.sounds[1].set("c3e3g3c4", "p", "4", "n", 15)
            pyxel.sounds[2].set("e3g3c4e4", "p", "4", "n", 15)
            pyxel.musics[0].set([1, 2], [], [], []) 
            pyxel.playm(0, loop=True)
        except Exception:
            pass

        pyxel.run(
            getattr(update_fn, "update"),
            getattr(draw_dn, "draw")
        )

    def reset_screen(self) -> None:
        pyxel.cls(0)

    def draw_menu(self) -> None:
        pyxel.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)

        # Twinkling space backdrop coordinate array mapping
        stars = [
            (11,8),(37,5),(61,19),(89,3),(113,14),(139,7),(157,22),(179,11),(199,6),(223,18),
            (241,9),(271,4),(293,17),(307,25),(13,35),(53,42),(97,38),(151,31),(197,44),(251,37),
            (17,55),(71,61),(127,58),(181,52),(229,63),(283,57),(43,75),(103,68),(163,72),(211,79),
            (29,92),(83,88),(149,95),(203,84),(257,91),(311,97),(7,108),(67,114),(131,101),(277,107),
            (23,125),(79,132),(137,119),(191,128),(239,121),(293,135),(41,148),(109,142),(167,155),(227,145),
            (19,165),(73,172),(143,161),(197,168),(253,175),(317,162),(47,185),(101,192),(173,183),(233,195),
            (31,205),(89,212),(157,202),(211,218),(269,208),(5,222),(59,228),(121,215),(179,225),(247,219),
        ]
        t = pyxel.frame_count
        for i, (sx, sy) in enumerate(stars):
            phase = (t + i * 7) % 30
            if phase < 5:
                col = 0 
            elif phase < 10:
                col = COL_GRAY
            elif phase < 20:
                col = COL_WHITE if i % 5 == 0 else (6 if i % 3 == 0 else COL_GRAY)
            else:
                col = COL_WHITE
            pyxel.pset(sx % SCREEN_WIDTH, sy % SCREEN_HEIGHT, col)

        pyxel.line(40, 30, 55, 22, 6)
        pyxel.pset(40, 30, COL_WHITE)
        pyxel.line(260, 60, 275, 52, 6)
        pyxel.pset(260, 60, COL_WHITE)

        # Draw structural logo borders
        pyxel.rect(24, 20, 272, 38, COL_DARK)
        pyxel.rectb(24, 20, 272, 38, 6)
        pyxel.rectb(22, 18, 276, 42, COL_BLUE)

        t1 = "* ZUMA TOWER DEFENSE *"
        t2 = "- Tower of Hell -"
        pyxel.text((SCREEN_WIDTH - len(t1) * 4) // 2, 27, t1, COL_YELLOW)
        pyxel.text((SCREEN_WIDTH - len(t2) * 4) // 2, 38, t2, COL_ORANGE)

        for dx, dy in [(34, 39), (SCREEN_WIDTH - 38, 39)]:
            pyxel.pset(dx,   dy-2, COL_YELLOW)
            pyxel.pset(dx-2, dy,   COL_YELLOW)
            pyxel.pset(dx+2, dy,   COL_YELLOW)
            pyxel.pset(dx,   dy+2, COL_YELLOW)
            pyxel.pset(dx,   dy,    COL_WHITE)

        # Selection Menu Panel Window Coordinates
        px, py, pw, ph = 74, 72, 172, 120
        pyxel.rect(px, py, pw, ph, COL_DARK)
        pyxel.rectb(px, py, pw, ph, 6)
        pyxel.rectb(px-2, py-2, pw+4, ph+4, COL_BLUE)

        for cx2, cy2 in [(px, py), (px+pw-1, py), (px, py+ph-1), (px+pw-1, py+ph-1)]:
            pyxel.pset(cx2, cy2, COL_YELLOW)

        entries = [
            ("[C]", "CAMPAIGN MODE",  COL_RED,    COL_YELLOW),
            ("[E]", "ENDLESS MODE",   COL_ORANGE, COL_GREEN),
            ("[L]", "LEADERBOARD",    6,          COL_WHITE),
            ("[Q]", "QUIT",           COL_RED,    COL_GRAY),
        ]
        for i, (key, label, key_col, lbl_col) in enumerate(entries):
            iy = py + 18 + i * 24
            ix = px + 16

            hovered = px + 6 <= pyxel.mouse_x <= px + pw - 6 and iy - 5 <= pyxel.mouse_y <= iy + 10

            if hovered:
                pyxel.rect(px + 6, iy - 5, pw - 12, 16, 0)
                pyxel.rectb(px + 6, iy - 5, pw - 12, 16, 6)
                pyxel.text(ix - 8, iy, ">", COL_YELLOW)

            pyxel.text(ix,      iy, key,   key_col if not hovered else COL_YELLOW)
            pyxel.text(ix + 18, iy, label, lbl_col if not hovered else COL_WHITE)

            if i < len(entries) - 1:
                for dot_x in range(px + 14, px + pw - 14, 4):
                    pyxel.pset(dot_x, iy + 13, COL_BLUE)

        pyxel.line(0, SCREEN_HEIGHT - 6, SCREEN_WIDTH, SCREEN_HEIGHT - 6, COL_BLUE)
        pyxel.line(0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, SCREEN_HEIGHT - 1, COL_BLUE)

    def draw_leaderboard(self, records: list[dict[str, Any]]) -> None:
        pyxel.text(110, 25, "TOP SCORERS", COL_YELLOW)
        if not records:
            pyxel.text(100, 80, "No records found.", COL_GRAY)
        else:
            for idx, entry in enumerate(records[:10]):
                y = 50 + (idx * 12)
                name = entry.get("name", "ANON")
                score = entry.get("score", 0)
                round_num = entry.get("round", 1)
                mode = entry.get("mode", "CAMPAIGN")
                display_str: str = f'{idx+1}. {name:<6} | XP: {score:<4} | R: {round_num} ({mode})'
                pyxel.text(60, y, display_str, COL_WHITE)
        pyxel.text(70, 200, "Press [M] to return to Main Menu", COL_GREEN)

    def draw_quit_confirm(self) -> None:
        pyxel.rect(50, 80, 220, 60, COL_DARK)
        pyxel.rectb(50, 80, 220, 60, COL_WHITE)
        pyxel.text(85, 95, "ARE YOU SURE YOU WANT TO QUIT?", COL_RED)
        pyxel.text(75, 115, "[Y] Confirm Quit   /   [N] Cancel", COL_WHITE)

    def draw_paths(self, paths: list[list[tuple[float, float]]]) -> None:
        for path in paths:
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i+1]
                pyxel.line(x1, y1, x2, y2, COL_BLUE)

    def draw_tunnels(self, tunnels: dict[int, list[tuple[float, float, float, float]]]) -> None:
        for path_idx, tunnel_list in tunnels.items():
            for tx, ty, tw, th in tunnel_list:
                pyxel.rect(tx, ty, tw, th, COL_GRAY)
                pyxel.rectb(tx, ty, tw, th, COL_WHITE)
            
    def draw_enemies(self, enemies: list[Enemy]) -> None:
        normal_sprites = {
            Color.RED: (32, 16),
            Color.ORANGE: (48, 16),
            Color.YELLOW: (0, 32),
            Color.GREEN: (16, 32),
            Color.BLUE: (32, 32),
            Color.VIOLET: (48, 32),
        }
        chameleon_sprites = {
            Color.RED: (16, 48),
            Color.ORANGE: (32, 48),
            Color.YELLOW: (48, 48),
            Color.GREEN: (0, 64),
            Color.BLUE: (16, 64),
            Color.VIOLET: (32, 64),
        }
        regenerator_sprite = (0, 48)

        for enemy in enemies:
            if enemy.status != EnemyStatus.ALIVE or enemy.x < -CELL_SIZE:
                continue
            ex = int(enemy.x) - ENEMY_HALF
            ey = int(enemy.y) - ENEMY_HALF
            
            etype = getattr(enemy, "enemy_type", None)
            if etype == EnemyType.REG:
                u, v = regenerator_sprite
            elif etype == EnemyType.CHM:
                u, v = chameleon_sprites.get(enemy.color, (16, 48))
            else:
                u, v = normal_sprites.get(enemy.color, (32, 16))
            
            # Draw sprite transparently masking out default pink borders (color index 6)
            pyxel.blt(ex, ey, 0, u, v, CELL_SIZE, CELL_SIZE, 6)

    def draw_bullets(self, bullets: list[Bullet]) -> None:
        bullet_sprites = {
            Color.RED: (0, 0),
            Color.ORANGE: (16, 0),
            Color.YELLOW: (32, 0),
            Color.GREEN: (48, 0), 
            Color.BLUE: (0, 16),
            Color.VIOLET: (16, 16),
        }
        for bullet in bullets:
            bx = int(bullet.x) - BULLET_RADIUS
            by = int(bullet.y) - BULLET_RADIUS
            u, v = bullet_sprites.get(bullet.color, (0, 0))
            pyxel.blt(bx, by, 0, u, v, BULLET_RADIUS*2, BULLET_RADIUS*2, 6)
 
    def draw_shooter(self, shooter_x: float, shooter_y: float, bullet_color: Color) -> None:
        sx = int(shooter_x)
        sy = int(shooter_y)
        pyxel.tri(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_WHITE)
        pyxel.trib(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_DARK)
        col = PYXEL_COLOR[bullet_color]
        pyxel.circ(sx, sy, 3, col)

    def draw_towers(self, rows: int, cols: int, grid: list[list[CellType]], tower_dirs: dict[tuple[int, int], Direction], selected: tuple[int, int] | None = None) -> None:
        for r in range(rows):
            for c in range(cols):
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                if grid[r][c] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                    is_upgraded = grid[r][c] == CellType.UPGRADED_TOWER
                    color = COL_ORANGE if not is_upgraded else COL_PURPLE
                    pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, color)

                    if selected == (r, c):
                        pyxel.rectb(x, y, CELL_SIZE, CELL_SIZE, COL_WHITE)
                    
                    dir_enum = tower_dirs.get((r, c), Direction.UP)
                    dir_str = {
                        Direction.UP:    "W",
                        Direction.DOWN:  "S",
                        Direction.LEFT:  "A",
                        Direction.RIGHT: "D",
                    }.get(dir_enum, "?")
                    pyxel.text(x + 2, y + 2, dir_str, COL_WHITE)
                    
                    if is_upgraded:
                        pyxel.text(x + 1, y + 9, "MAX", COL_YELLOW)
                    else:
                        pyxel.text(x + 1, y + 9, "[U]", COL_WHITE)
 
    def draw_hud(self, user_hp: int, total_exp: int, curr_round: int, max_rounds: int, state: GameState, pending_direction: Direction, selected_tower: tuple[int, int] | None = None, game_mode: GameMode = GameMode.CAMPAIGN) -> None:
        pyxel.text(4, 4,  f"HP:  {user_hp}", COL_WHITE)
        pyxel.text(4, 12, f"EXP: {total_exp}", COL_WHITE)
        if game_mode == GameMode.ENDLESS:
            pyxel.text(4, 20, f"Round: {curr_round} (Endless)", COL_WHITE)
        else:
            pyxel.text(4, 20, f"Round: {curr_round}/{max_rounds}", COL_WHITE)
      
        if state == GameState.ROUND_PENDING: 
            pyxel.rect(0, 180, SCREEN_WIDTH, 60, COL_DARK)
            pyxel.text(8, 185, f"ROUND {curr_round} COMPLETE!", COL_WHITE)
            
            dir_label = {
                Direction.UP:    "UP (W)",
                Direction.DOWN:  "DOWN (S)",
                Direction.LEFT:  "LEFT (A)",
                Direction.RIGHT: "RIGHT (D)",
            }.get(pending_direction, "?")
 
            if selected_tower:
                pyxel.text(8, 198, f"Selected tower dir (WASD): {dir_label}", COL_YELLOW)
            else:
                pyxel.text(8, 198, f"Next Tower Dir (WASD): {dir_label}",     COL_YELLOW)

            pyxel.text(8, 208, "Click grid to place Tower (5 EXP)", COL_YELLOW)
            pyxel.text(8, 218, "Click tower to upgrade (5 EXP)", COL_ORANGE)
            
            pyxel.text(200, 198, "SPACE - Start Round!", COL_GREEN)
            pyxel.text(200, 208, "[M] - Main Menu", COL_GRAY)
            pyxel.text(200, 218, "[Q] - Quit", COL_GRAY)
        
        elif state == GameState.PAUSED:
            pyxel.rect(60, 90, 200, 50, COL_DARK)
            pyxel.rectb(60, 90, 200, 50, COL_WHITE)
            pyxel.text(110, 100, "PAUSED",              COL_YELLOW)
            pyxel.text(75,  115, "[P] or click RESUME", COL_WHITE)
            pyxel.text(75,  125, "[Q] Quit (no save)",  COL_GRAY)

    def draw_pause_button(self, is_paused: bool) -> None:
        btnx = SCREEN_WIDTH // 2 - 25
        btny = 4
        pyxel.rect(btnx, btny, 50, 13, COL_GRAY)
        pyxel.rectb(btnx, btny, 50, 13, COL_WHITE)
        text = "RESUME" if is_paused else "PAUSE"
        pyxel.text(btnx + 13, btny + 4, text, COL_WHITE)
 
    def draw_game_over(self, total_exp: int, user_hp: int) -> None:
        pyxel.rect(55, 85, 210, 75, COL_DARK)
        pyxel.rectb(55, 85, 210, 75, COL_WHITE)
        
        if user_hp <= 0:
            pyxel.text(100, 95,  "GAME OVER",              COL_RED)
            pyxel.text(75,  108, f"Final EXP: {total_exp}", COL_WHITE)
        else:
            pyxel.text(100, 95,  "YOU WIN!",               COL_GREEN)
            pyxel.text(75,  108, f"Total EXP: {total_exp}", COL_WHITE)
            
        pyxel.text(70, 122, "[M] Main Menu", COL_GRAY)
        pyxel.text(70, 133, "[R] Play Again", COL_YELLOW)
        pyxel.text(70, 144, "[Q] Quit",       COL_GRAY)

    def draw_confirm_reset(self) -> None:
        pyxel.rect(40, 90, 240, 55, COL_DARK)
        pyxel.rectb(40, 90, 240, 55, COL_WHITE)
        pyxel.text(70,  99, "Reset game and return to menu?", COL_YELLOW)
        pyxel.text(70, 112, "All progress will be lost!",     COL_RED)
        pyxel.text(70, 125, "[Y] Yes, reset   [N] Cancel",    COL_WHITE)

    def draw_confirm_menu(self) -> None:
        pyxel.rect(40, 90, 240, 55, COL_DARK)
        pyxel.rectb(40, 90, 240, 55, COL_WHITE)
        pyxel.text(70,  99, "Return to Main Menu?",         COL_YELLOW)
        pyxel.text(70, 112, "All progress will be lost!",   COL_RED)
        pyxel.text(70, 125, "[Y] Yes, go back   [N] Cancel", COL_WHITE)