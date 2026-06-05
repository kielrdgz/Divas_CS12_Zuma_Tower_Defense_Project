#pyright: strict

from __future__ import annotations
import pyxel
from model import ZumaTowerModel
from view import ZumaTowerView
from data import *
    
class ZumaTowerController:
    def __init__(self, model: ZumaTowerModel, view: ZumaTowerView):
        self._model = model
        self._view = view

        self._selected_tower: tuple[int, int] | None = None
        self._tower_menu_open: bool = False
        self._pending_tower_cell: tuple[int, int] | None = None

    def start_game(self) -> None:
        self._view.start_game(self, self) # update, draw

    def _is_pause_clicked(self) -> bool:
        btnx = SCREEN_WIDTH // 2 - 25
        btny = 4
        return (btnx <= pyxel.mouse_x <= btnx + 50) and (btny <= pyxel.mouse_y <= btny + 13) # did cursor click pause/resume button

    def update(self) -> None:
        state = self._model.state
        
        # confirm reset dialog
        if state == GameState.CONFIRM_RESET:
            if pyxel.btnp(pyxel.KEY_Y):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_N):
                self._model.cancel_confirm()
            return None
        
        # confirm menu dialog
        if state == GameState.CONFIRM_MENU:
            if pyxel.btnp(pyxel.KEY_Y):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_N):
                self._model.cancel_confirm()
            return None
        
        # game over screen
        if self._model.is_game_over:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_R):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            return None
        
        # menu
        if state == GameState.MENU:
            if pyxel.btnp(pyxel.KEY_C):
                self._model.set_game_mode(GameMode.CAMPAIGN)
                self._model.set_state(GameState.ROUND_PENDING)
            elif pyxel.btnp(pyxel.KEY_E):
                self._model.set_game_mode(GameMode.ENDLESS)
                self._model.set_state(GameState.ROUND_PENDING)
            elif pyxel.btnp(pyxel.KEY_L):
                self._model.set_state(GameState.LEADERBOARD)
            elif pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            return None
        
        # leaderboard
        if state == GameState.LEADERBOARD:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.set_state(GameState.MENU)
            return None
        
        # paused
        if state == GameState.PAUSED:
            if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_SPACE):
                self._model.resume()
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_pause_clicked():
                self._model.resume()
            elif pyxel.btnp(pyxel.KEY_M):
                self._model.open_confirm_menu()
            elif pyxel.btnp(pyxel.KEY_R):
                self._model.open_confirm_reset()
            elif pyxel.btnp(pyxel.KEY_Q):
                self._model.open_confirm_reset()
            return None

        # pause button / p key from ongoing
        if pyxel.btnp(pyxel.KEY_P):
            if state == GameState.ONGOING:
                self._model.set_state(GameState.PAUSED)
                return None
 
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_pause_clicked():
            if state == GameState.ONGOING:
                self._model.set_state(GameState.PAUSED)
                return None
            
        # ongoing
        if state == GameState.ONGOING:
            if pyxel.btnp(pyxel.KEY_Q):
                self._model.open_confirm_reset()
                return None

            if pyxel.btnp(pyxel.KEY_M):
                self._model.open_confirm_menu()
                return None
            
            kills_before = self._model.tot_killed
            self._model.update()
            if self._model.tot_killed > kills_before:
                try:
                    pyxel.play(3, 0)
                except Exception:
                    pass
 
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not self._is_pause_clicked():
                self._model.shoot(float(pyxel.mouse_x), float(pyxel.mouse_y))
 
            if self._selected_tower and self._model.grid[self._selected_tower[0]][self._selected_tower[1]] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                if pyxel.btnp(pyxel.KEY_W): self._model._tower_directions[self._selected_tower] = Direction.UP
                elif pyxel.btnp(pyxel.KEY_S): self._model._tower_directions[self._selected_tower] = Direction.DOWN
                elif pyxel.btnp(pyxel.KEY_A): self._model._tower_directions[self._selected_tower] = Direction.LEFT
                elif pyxel.btnp(pyxel.KEY_D): self._model._tower_directions[self._selected_tower] = Direction.RIGHT
            else:
                if pyxel.btnp(pyxel.KEY_W): self._model.set_all_towers_direction(Direction.UP)
                elif pyxel.btnp(pyxel.KEY_S): self._model.set_all_towers_direction(Direction.DOWN)
                elif pyxel.btnp(pyxel.KEY_A): self._model.set_all_towers_direction(Direction.LEFT)
                elif pyxel.btnp(pyxel.KEY_D): self._model.set_all_towers_direction(Direction.RIGHT)
            return None
        
        # gameover
        if state == GameState.GAMEOVER:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_R):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            return None
        
        # round pending
        if state == GameState.ROUND_PENDING:
            if pyxel.btnp(pyxel.KEY_Q):
                self._model.open_confirm_reset()
                return None
 
            if pyxel.btnp(pyxel.KEY_R):
                self._model.open_confirm_reset()
                return None
 
            if pyxel.btnp(pyxel.KEY_M):
                self._model.open_confirm_menu()
                return None
 
            if pyxel.btnp(pyxel.KEY_SPACE):
                self._model.start_next_round()
                return None
 
            col = pyxel.mouse_x // CELL_SIZE
            row = pyxel.mouse_y // CELL_SIZE
 
            if 0 <= row < self._model.rows and 0 <= col < self._model.cols:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                    if self._model.grid[row][col] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                        self._model.try_remove_tower(row, col)
                        if self._selected_tower == (row, col):
                            self._selected_tower = None
 
                elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    if self._model.grid[row][col] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                        self._selected_tower = (row, col)
                        self._model.try_upgrade_tower(row, col)
                    elif self._model.grid[row][col] == CellType.EMPTY:
                        current_direction = self._model.pending_direction
                        self._model.try_place_tower(row, col)
                        if self._model.grid[row][col] == CellType.TOWER:
                            self._model._tower_directions[(row, col)] = current_direction
                            self._selected_tower = (row, col)
 
            if self._selected_tower and self._model.grid[self._selected_tower[0]][self._selected_tower[1]] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                if pyxel.btnp(pyxel.KEY_W): self._model._tower_directions[self._selected_tower] = Direction.UP
                elif pyxel.btnp(pyxel.KEY_S): self._model._tower_directions[self._selected_tower] = Direction.DOWN
                elif pyxel.btnp(pyxel.KEY_A): self._model._tower_directions[self._selected_tower] = Direction.LEFT
                elif pyxel.btnp(pyxel.KEY_D): self._model._tower_directions[self._selected_tower] = Direction.RIGHT
            else:
                if pyxel.btnp(pyxel.KEY_W): self._model.set_pending_direction(Direction.UP)
                elif pyxel.btnp(pyxel.KEY_S): self._model.set_pending_direction(Direction.DOWN)
                elif pyxel.btnp(pyxel.KEY_A): self._model.set_pending_direction(Direction.LEFT)
                elif pyxel.btnp(pyxel.KEY_D): self._model.set_pending_direction(Direction.RIGHT)
 
    def draw(self) -> None:
        self._view.reset_screen()

        if self._model.state == GameState.MENU:
            self._view.draw_menu()
            return None
        
        elif self._model.state == GameState.LEADERBOARD:
            records = getattr(self._model, "leaderboard_records", [])
            self._view.draw_leaderboard(records)
            return None
        
        self._view.draw_paths(self._model.paths)
        self._view.draw_towers(self._model.rows, self._model.cols, self._model.grid, self._model._tower_directions)
        if self._model.state != GameState.ROUND_PENDING:
            self._view.draw_enemies(self._model.enemies) 
        self._view.draw_tunnels(self._model.tunnels)
        if self._model.state != GameState.ROUND_PENDING:
            self._view.draw_bullets(self._model.bullets)
        self._view.draw_shooter(self._model.shooter_x, self._model.shooter_y, self._model.bullet_color)
        self._view.draw_hud(self._model.user_hp, self._model.total_exp, self._model.curr_round, self._model.max_rounds, self._model.state, self._model.pending_direction, self._model._game_mode)
            
        if self._model.state in (GameState.ONGOING, GameState.PAUSED):
            self._view.draw_pause_button(self._model.state == GameState.PAUSED)
        
        if self._model.state == GameState.ROUND_PENDING:
            if self._tower_menu_open and self._selected_tower:
                r, c = self._selected_tower
                is_upgraded = self._model.grid[r][c] == CellType.UPGRADED_TOWER
                self._view.draw_tower_menu(r, c, is_upgraded, self._model.total_exp)
            if self._pending_tower_cell:
                r, c = self._pending_tower_cell
                self._view.draw_place_confirm(r, c, self._model.total_exp)

        if self._model.state == GameState.CONFIRM_RESET:
            self._view.draw_confirm_reset()

        if self._model.state == GameState.CONFIRM_MENU:
            self._view.draw_confirm_menu()
            
        if self._model.state == GameState.QUIT_CONFIRM:
            self._view.draw_quit_confirm()

        if self._model.is_game_over:
            self._view.draw_game_over(self._model.total_exp, self._model.user_hp)
            
    def draw_tower_menu(self, row: int, col: int, upgrade_level: int, exp: int) -> None:
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        box_w = 120
        box_h = 70
        
        bx = x - 10
        by = y - box_h - 4
        
        pyxel.rect(bx, by, box_w, box_h, COL_DARK)
        pyxel.rectb(bx, by, box_w, box_h, COL_WHITE)
        pyxel.text(bx + 4, by + 4,  "TOWER OPTIONS", COL_YELLOW)
        pyxel.text(bx + 4, by + 16, "WASD - Set Direction", COL_WHITE)
        
        if upgrade_level == 0:
            col_u = COL_GREEN if exp >= 10 else COL_GRAY
            pyxel.text(bx + 4, by + 26, "[U] Upgrade to Lv2 (10 XP)", col_u)
        elif upgrade_level == 1:
            col_u = COL_GREEN if exp >= 20 else COL_GRAY
            pyxel.text(bx + 4, by + 26, "[U] Upgrade to Lv3 (20 XP)", col_u)
        else:
            pyxel.text(bx + 4, by + 26, "Max Level Reached", COL_GRAY)
        
        pyxel.text(bx + 4, by + 44, "[R] Remove Tower (+5 EXP)", COL_RED)
        pyxel.text(bx + 4, by + 54, "[X/Right Click] Close", COL_GRAY)
        
    def draw_place_confirm(self, row: int, col: int, exp: int) -> None:
        can_afford = exp >= 5
        cost_col = COL_GREEN if can_afford else COL_RED
        pyxel.text(bx + 4, by + 4,  "Place tower here?", COL_YELLOW)
        pyxel.text(bx + 4, by + 14, "Cost: 5 EXP", cost_col)
            
        if not can_afford:
            pyxel.text(bx + 4, by + 24, "Not enough EXP!", COL_RED)
        else:
            pyxel.text(bx + 4, by + 24, "[Y] Yes  [N] No", COL_WHITE)