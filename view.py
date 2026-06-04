#pyright: strict

from __future__ import annotations

import pyxel
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
    def start_game(self, update_fn: object, draw_dn: object) -> None:
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Zuma Tower Defense", fps=FPS)
        pyxel.mouse(True)

        pyxel.load("assets.pyxres")
        
        try:
            pyxel.sounds[0].set("a3a2c1", "p", "7", "s", 5) 
            
            pyxel.sounds[1].set("c3e3g3c4", "p", "4", "n", 15)
            pyxel.sounds[2].set("e3g3c4e4", "p", "4", "n", 15)
            pyxel.musics[0].set([1, 2], [], [], []) 
            pyxel.playm(0, loop=True) # play music on loop
        except Exception:
            pass


        pyxel.run(
            getattr(update_fn, "update"),
            getattr(draw_dn, "draw")
        )

    def reset_screen(self):
        pyxel.cls(0)

    def draw_menu(self) -> None:
        # yehey main menu!
        pyxel.text(105, 50, "ZUMA TOWER OF HELL", COL_YELLOW)

        pyxel.text(85, 90, "Press [C] - Campaign Mode", COL_WHITE)
        pyxel.text(85, 105, "Press [E] - Endless Mode", COL_WHITE)
        pyxel.text(85, 120, "Press [L] - Leaderboard", COL_BLUE)

    def draw_leaderboard(self, records: list[dict[str, Any]]) -> None:
        pyxel.text(110, 25, "TOP SCORERS", COL_YELLOW)
        if not records:
            pyxel.text(100, 80, "No records found.", COL_GRAY)
        else:
            for id, entry in enumerate(records[:10]): # can change to whole
                y = 50 + (idx * 12)
                name = entry.get("name", "ANON")
                score = entry.get("score", 0)
                round_num = entry.get("round", 1)
                mode = entry.get("mode", "CAMPAIGN")
                display_tr: str = f'{id+1}. {name:<6} | XP: {score:<4} | R: {round_num} ({mode})'
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
                x1, y1 = path[i]  # start point of segment
                x2, y2 = path[i+1]  # end point of segment
                
                pyxel.line(x1, y1, x2, y2, COL_BLUE)  # draw straight line between points

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
            ex = round(enemy.x) - ENEMY_HALF
            ey = round(enemy.y) - ENEMY_HALF
            u, v = (32, 16)
            
            etype = getattr(enemy, "_enemy_type", None)
            if etype == EnemyType.REG:
                u, v = regenerator_sprite
            elif etype == EnemyType.CHM:
                u, v = chameleon_sprites.get(enemy.color, (16, 48))
            else:
                u, v = normal_sprites.get(enemy.color, (32, 16))
            
            pyxel.blt(ex, ey, 0, u, v, CELL_SIZE, CELL_SIZE, 6)

            # col = PYXEL_COLOR[enemy.color]
            # ex = int(enemy.x)
            # ey = int(enemy.y)
            # pyxel.rect(ex - ENEMY_HALF, ey - ENEMY_HALF,
            #            ENEMY_HALF * 2, ENEMY_HALF * 2, col)  # filled
            # pyxel.rectb(ex - ENEMY_HALF, ey - ENEMY_HALF,
            #             ENEMY_HALF * 2, ENEMY_HALF * 2, COL_DARK)  # outline
 
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
            bx = round(bullet.x) - BULLET_RADIUS
            by = round(bullet.y) - BULLET_RADIUS

            u, v = bullet_sprites.get(bullet.color, (0, 0))
            pyxel.blt(bx, by, 0, u, v, BULLET_RADIUS*2, BULLET_RADIUS*2, 6)

            # col = PYXEL_COLOR[bullet.color]
            # pyxel.circ(int(bullet.x), int(bullet.y), BULLET_RADIUS, col)
 
    def draw_shooter(self, shooter_x: float, shooter_y: float, bullet_color: Color) -> None:
        sx = int(shooter_x)
        sy = int(shooter_y)
        pyxel.tri(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_WHITE)  # white triangle filled
        pyxel.trib(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_DARK)  # outline
        col = PYXEL_COLOR[bullet_color]
        pyxel.circ(sx, sy, 3, col)  # shows next bullet color

    def draw_towers(self, rows: int, cols: int, grid: list[list[CellType]], tower_dirs: dict[tuple[int, int], Direction], selected: tuple[int, int] | None = None) -> None:
        for r in range(rows):  # scans grid for towers
            for c in range(cols):
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                if grid[r][c] in (CellType.TOWER, CellType.UPGRADED_TOWER):              # can still change colors of towers since medyo similar with bullets
                    color = COL_ORANGE if grid[r][c] == CellType.TOWER else COL_PURPLE
                    pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, color)

                    if selected == (r, c):
                        pyxel.rectb(x, y, CELL_SIZE, CELL_SIZE, COL_WHITE)
                    
                    # Look up this specific tower's pointing vector layout direction string
                    dir_enum = tower_dirs.get((r, c), Direction.UP)
                    dir_str = {
                        Direction.UP:    "W",
                        Direction.DOWN:  "S",
                        Direction.LEFT:  "A",
                        Direction.RIGHT: "D",
                    }.get(dir_enum, "?")
                    pyxel.text(x + 6, y + 5, dir_str, COL_WHITE)

                #     pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, 9) # orange block for normal tower
                # elif grid[r][c] == CellType.UPGRADED_TOWER:
                #     pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, 2) # purple block for upgraded tower
 
    def draw_hud(self, user_hp: int, total_exp: int, curr_round: int, max_rounds: int, state: GameState, pending_direction: Direction, selected_tower: tuple[int, int] | None= None, game_mode: GameMode = GameMode.CAMPAIGN) -> None:
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
                pyxel.text(8, 194, f"Tower dir (WASD): {dir_label}", COL_YELLOW)
                pyxel.text(8, 204, "Click tower for options",        COL_YELLOW)
            else:
                pyxel.text(8, 198, f"Next Tower Dir (WASD): {dir_label}", COL_YELLOW)
                pyxel.text(8, 204, "Click empty cell to place (5 EXP)",   COL_YELLOW)

            pyxel.text(8, 214, "Right-click tower to remove", COL_ORANGE)
            pyxel.text(200, 198, "SPACE - Start Round!",      COL_GREEN)
            pyxel.text(200, 208, "[M] - Main Menu",           COL_WHITE)
            pyxel.text(200, 218, "[Q] - Quit",                COL_GRAY)
        
        elif state == GameState.PAUSED:
            pyxel.rect(60, 90, 200, 60, COL_DARK)
            pyxel.rectb(60, 90, 200, 60, COL_WHITE)
            pyxel.text(110, 100, "PAUSED",              COL_YELLOW)
            pyxel.text(75,  113, "[P] or click RESUME", COL_GREEN)
            pyxel.text(75,  123, "[M] Main Menu",       COL_WHITE)
            pyxel.text(75,  133, "[Q] Quit (No save)",  COL_GRAY)

    def draw_pause_button(self, is_paused: bool) -> None:
        btnx = SCREEN_WIDTH // 2 - 25
        btny = 4
        pyxel.rect(btnx, btny, 50, 13, COL_GRAY)
        pyxel.rectb(btnx, btny, 50, 13, COL_WHITE)
        text = "RESUME" if is_paused else "PAUSE"
        pyxel.text(btnx + 13, btny + 4, text, COL_WHITE)
 
    def draw_game_over(self, total_exp: int, user_hp: int) -> None:
        pyxel.rect(60, 90, 200, 60, COL_DARK)
        pyxel.rectb(60, 90, 200, 60, COL_WHITE)
        
        if user_hp <= 0:
            pyxel.text(100, 105, "GAME OVER",               COL_RED)
            pyxel.text(80,  117, f"Final EXP: {total_exp}", COL_WHITE)
        else:
            pyxel.text(100, 105, "YOU WIN!",                COL_GREEN)
            pyxel.text(80,  117, f"Total EXP: {total_exp}", COL_WHITE)
            
        pyxel.text(85, 125, "[M] Back to Main Menu",        COL_WHITE)
        pyxel.text(85, 137, "[Q] Quit Game",                COL_GRAY)

    def draw_tower_menu(self, row: int, col: int, is_upgraded: bool, exp: int) -> None:
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        box_w = 120
        box_h = 70
        
        # position box above the tower, but it wont go off screen
        bx = x - 10
        by = y - box_h - 4

        bx = max(0, min(bx, SCREEN_WIDTH - box_w))
        by = max(0, min(by, SCREEN_HEIGHT - box_h))

        pyxel.rect(bx, by, box_w, box_h, COL_DARK)
        pyxel.rectb(bx, by, box_w, box_h, COL_WHITE)
        
        # actual box content
        pyxel.text(bx + 4, by + 4,  "TOWER OPTIONS",        COL_YELLOW)
        pyxel.text(bx + 4, by + 16, "WASD - Set Direction", COL_WHITE)
        if not is_upgraded:
            col_u = COL_GREEN if exp >= 5 else COL_GRAY
            pyxel.text(bx + 4, by + 26, "[U] Upgrade (5 EXP)", col_u)
        else:
            pyxel.text(bx + 4, by + 26, "Already upgraded",      COL_GRAY)
        pyxel.text(bx + 4, by + 44, "[R] Remove Tower (+5 EXP)", COL_RED)
        pyxel.text(bx + 4, by + 54, "[X/Right Click] Close",     COL_GRAY)

    def draw_place_confirm(self, row: int, col: int, exp: int) -> None:
        # same size and position logic with draw_tower_menu
        x = col * CELL_SIZE
        y = row * CELL_SIZE

        box_w = 110
        box_h = 40

        bx = x - 10
        by = y - box_h - 4

        bx = max(0, min(bx, SCREEN_WIDTH - box_w))
        by = max(0, min(by, SCREEN_HEIGHT - box_h))

        pyxel.rect(bx, by, box_w, box_h, COL_DARK)
        pyxel.rectb(bx, by, box_w, box_h, COL_WHITE)

        can_afford = exp >= 5
        cost_col = COL_GREEN if can_afford else COL_RED

        pyxel.text(bx + 4, by + 4,  "Place tower here?",   COL_YELLOW)
        pyxel.text(bx + 4, by + 14, "Cost: 5 EXP",         cost_col)
        if not can_afford:
            pyxel.text(bx + 4, by + 24, "Not enough EXP!",  COL_RED)
        else:
            pyxel.text(bx + 4, by + 24, "[Y] Yes  [N] No",  COL_WHITE)