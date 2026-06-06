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
        elif state == GameState.CONFIRM_MENU:
            if pyxel.btnp(pyxel.KEY_Y):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_N):
                self._model.cancel_confirm()
            return None
        
        # open shop in main menu
        elif state == GameState.MAIN_MENU_SHOP:
            if pyxel.btnp(pyxel.KEY_X):
                self._model.set_state(GameState.MENU)
            elif pyxel.btnp(pyxel.KEY_1):
                self._model.buy_powerup(PowerupType.MEGA_BULLET)
            elif pyxel.btnp(pyxel.KEY_2):
                self._model.buy_powerup(PowerupType.STAR)
            elif pyxel.btnp(pyxel.KEY_3):
                self._model.buy_powerup(PowerupType.TOWER_FRENZY)
            return None

        # ask for name input for leaderbaord
        elif state == GameState.NAME_INPUT:
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key) and len(self._model._nickname) < 8:
                    self._model._nickname += chr(key - pyxel.KEY_A + 65)
                    
            if pyxel.btnp(pyxel.KEY_BACKSPACE) and len(self._model._nickname) > 0:
                self._model._nickname = self._model._nickname[:-1]
                
            if pyxel.btnp(pyxel.KEY_RETURN) and len(self._model._nickname) > 0:
                self._model.save_leaderboard()
                self._model.set_state(GameState.NAME_INPUT_DONE)
            return None

        # done typing name for leaderboard
        elif state == GameState.NAME_INPUT_DONE:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_L):
                self._model.set_state(GameState.LEADERBOARD)
            return None

        # edit settings of enemy count and hp count
        elif state == GameState.SETTINGS:
            if pyxel.btnp(pyxel.KEY_UP): 
                self._model._max_hp += 1
            if pyxel.btnp(pyxel.KEY_DOWN): 
                self._model._max_hp = max(1, self._model._max_hp - 1)
            if pyxel.btnp(pyxel.KEY_RIGHT): 
                self._model._settings_enemies += 1
            if pyxel.btnp(pyxel.KEY_LEFT): 
                self._model._settings_enemies = max(1, self._model._settings_enemies - 1)
            
            if pyxel.btnp(pyxel.KEY_M):
                self._model.save_settings()
                self._model.set_state(GameState.MENU)
            return None
        
        # pause
        if pyxel.btnp(pyxel.KEY_P) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_pause_clicked()):
            if self._model.state == GameState.ONGOING:
                self._model.set_state(GameState.PAUSED)
            elif self._model.state == GameState.PAUSED:
                self._model.resume()
            return None

        # state
        if self._model.state == GameState.MENU:
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            clicked = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            
            if pyxel.btnp(pyxel.KEY_C) or (clicked and 74 <= mx <= 246 and 85 <= my <= 101):
                self._model.set_game_mode(GameMode.CAMPAIGN)
                self._model.start_round_one()
                
            elif pyxel.btnp(pyxel.KEY_E) or (clicked and 74 <= mx <= 246 and 109 <= my <= 125):
                self._model.set_game_mode(GameMode.ENDLESS)
                self._model.start_round_one()
                
            elif pyxel.btnp(pyxel.KEY_L) or (clicked and 74 <= mx <= 246 and 133 <= my <= 149):
                self._model.set_state(GameState.LEADERBOARD)

            elif pyxel.btnp(pyxel.KEY_B) or (clicked and 74 <= mx <= 246 and 157 <= my <= 173):
                self._model.set_state(GameState.MAIN_MENU_SHOP)

            elif pyxel.btnp(pyxel.KEY_S) or (clicked and 74 <= mx <= 246 and 181 <= my <= 197): 
                self._model.set_state(GameState.SETTINGS)
            
            elif pyxel.btnp(pyxel.KEY_Q) or (clicked and 74 <= mx <= 246 and 205 <= my <= 220):
                pyxel.quit()
                
            return None

        elif self._model.state == GameState.LEADERBOARD:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.set_state(GameState.MENU)
            return None

        elif self._model.state == GameState.PAUSED:
            if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_SPACE) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_pause_clicked()): # continues
                self._model.resume()
            elif pyxel.btnp(pyxel.KEY_M): 
                self._model.open_confirm_menu()
            elif pyxel.btnp(pyxel.KEY_Q):
                self._model.open_confirm_reset()
            return None
            
        elif self._model.state == GameState.GAMEOVER:
            if pyxel.btnp(pyxel.KEY_M) or pyxel.btnp(pyxel.KEY_R):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            return None
                
        elif self._model.state == GameState.ROUND_PENDING:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self._model.start_next_round()
                self._selected_tower = None
                self._tower_menu_open = False
                self._pending_tower_cell = None
                return None

            if pyxel.btnp(pyxel.KEY_M):
                self._model.open_confirm_menu()

            if pyxel.btnp(pyxel.KEY_Q):
                if self._model._game_mode == GameMode.ENDLESS:
                    self._model.save_leaderboard_partial()
                self._model.open_confirm_reset()
                return None
            
            if pyxel.btnp(pyxel.KEY_B) and not self._tower_menu_open: # B for buy kasi gamit na yung S
                self._model.set_state(GameState.SHOP)
                return None
            
            if pyxel.btnp(pyxel.KEY_I):
                self._model.open_inventory()
                return None


            col = pyxel.mouse_x // CELL_SIZE
            row = pyxel.mouse_y // CELL_SIZE

            if 0 <= row < self._model.rows and 0 <= col < self._model.cols:
                if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                    self._model.try_remove_tower(row, col)
                    if self._selected_tower == (row, col):
                        self._selected_tower = None
                        self._tower_menu_open = False
                elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    if self._model.grid[row][col] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                        if self._selected_tower == (row, col):
                            self._tower_menu_open = True
                        else:
                            self._selected_tower = (row, col)
                            self._tower_menu_open = False
                        self._pending_tower_cell = None
                    elif self._model.grid[row][col] == CellType.EMPTY:
                        self._selected_tower = None
                        self._tower_menu_open = False
                        self._pending_tower_cell = (row, col)

            if pyxel.btnp(pyxel.KEY_X):
                self._selected_tower = None
                self._tower_menu_open = False
                self._pending_tower_cell = None

            if self._pending_tower_cell:
                if pyxel.btnp(pyxel.KEY_Y):
                    row_p, col_p = self._pending_tower_cell
                    if self._model.try_place_tower(row_p, col_p):
                        self._selected_tower = (row_p, col_p)
                    else:
                        self._selected_tower = None 
                    self._pending_tower_cell = None
                elif pyxel.btnp(pyxel.KEY_N) or pyxel.btnp(pyxel.KEY_X):
                    self._pending_tower_cell = None

            if self._tower_menu_open and self._selected_tower:
                r, c = self._selected_tower
                if pyxel.btnp(pyxel.KEY_U):
                    self._model.try_upgrade_tower(r, c)
                    self._tower_menu_open = False
                elif pyxel.btnp(pyxel.KEY_R):
                    self._model.try_remove_tower(r, c)
                    self._selected_tower = None
                    self._tower_menu_open = False

                elif pyxel.btnp(pyxel.KEY_X):
                    self._tower_menu_open = False
                elif pyxel.btnp(pyxel.KEY_W): 
                    self._model.change_spec_tower_dir(r, c, Direction.UP)
                elif pyxel.btnp(pyxel.KEY_S): 
                    self._model.change_spec_tower_dir(r, c, Direction.DOWN)
                elif pyxel.btnp(pyxel.KEY_A): 
                    self._model.change_spec_tower_dir(r, c, Direction.LEFT)
                elif pyxel.btnp(pyxel.KEY_D): 
                    self._model.change_spec_tower_dir(r, c, Direction.RIGHT)
            else:
                if pyxel.btnp(pyxel.KEY_W): 
                    self._model.set_pending_direction(Direction.UP)
                elif pyxel.btnp(pyxel.KEY_S): 
                    self._model.set_pending_direction(Direction.DOWN)
                elif pyxel.btnp(pyxel.KEY_A): 
                    self._model.set_pending_direction(Direction.LEFT)
                elif pyxel.btnp(pyxel.KEY_D): 
                    self._model.set_pending_direction(Direction.RIGHT)
            return None

        elif self._model.state == GameState.ONGOING:
            kills_before = self._model.tot_killed
            self._model.update()
            
            if self._model.tot_killed > kills_before: # sfx for killing enemies but should probably be moved to view
                try:
                    pyxel.play(3, 0) 
                except Exception:
                    pass

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): 
                self._model.shoot(float(pyxel.mouse_x), float(pyxel.mouse_y))

            if pyxel.btnp(pyxel.KEY_I):
                self._model.open_inventory()
                return None

            if pyxel.btnp(pyxel.KEY_Q):
                if self._model.game_mode == GameMode.ENDLESS:
                    self._model.save_leaderboard_partial()
                self._model.open_confirm_reset()
            elif pyxel.btnp(pyxel.KEY_M):
                self._model.open_confirm_menu()
            return None
        
        elif self._model.state == GameState.SHOP:
            if pyxel.btnp(pyxel.KEY_X):
                self._model.set_state(GameState.ROUND_PENDING)
            elif pyxel.btnp(pyxel.KEY_1):
                self._model.buy_powerup(PowerupType.MEGA_BULLET)
            elif pyxel.btnp(pyxel.KEY_2):
                self._model.buy_powerup(PowerupType.STAR)
            elif pyxel.btnp(pyxel.KEY_3):
                self._model.buy_powerup(PowerupType.TOWER_FRENZY)
            return None

        elif self._model.state == GameState.INVENTORY:
            if pyxel.btnp(pyxel.KEY_X):
                self._model.set_state(self._model._prev_state)
            elif self._model._prev_state == GameState.ONGOING:
                if pyxel.btnp(pyxel.KEY_1):
                    self._model.set_state(GameState.ONGOING)
                    self._model.activate_powerup(PowerupType.MEGA_BULLET)
                elif pyxel.btnp(pyxel.KEY_2):
                    self._model.set_state(GameState.ONGOING)
                    self._model.activate_powerup(PowerupType.STAR)
                elif pyxel.btnp(pyxel.KEY_3):
                    self._model.set_state(GameState.ONGOING)
                    self._model.activate_powerup(PowerupType.TOWER_FRENZY)
            return None

    def draw(self) -> None:
        self._view.reset_screen()

        if self._model.state == GameState.MENU:
            self._view.draw_menu(self._model.coins)
            return None
        
        elif self._model.state == GameState.MAIN_MENU_SHOP:
            self._view.draw_shop(self._model.coins, self._model.inventory)
            return None
        
        elif self._model.state == GameState.LEADERBOARD:
            self._view.draw_leaderboard(self._model.load_raw_leaderboard())
            return None
        
        elif self._model.state == GameState.SETTINGS:
            self._view.draw_settings(self._model._max_hp, self._model._settings_enemies)
            return None
        
        self._view.draw_paths(self._model.paths)
        
        tower_map = {(t.r, t.c): t for t in self._model._active_towers}
        self._view.draw_towers(self._model.rows, self._model.cols, self._model.grid, self._model._tower_directions, self._model.tower_levels, self._selected_tower) # tower_map
        
        if self._model.state != GameState.ROUND_PENDING:
            self._view.draw_enemies(self._model.enemies) 
        self._view.draw_tunnels(self._model.tunnels)
        if self._model.state != GameState.ROUND_PENDING:
            self._view.draw_bullets(self._model.bullets)
        self._view.draw_shooter(self._model.shooter_x, self._model.shooter_y, self._model.bullet_color)
        self._view.draw_hud(self._model.user_hp, self._model.total_exp, self._model.coins, self._model.curr_round, self._model.max_rounds, self._model.state, self._model.pending_direction, self._selected_tower, self._model._game_mode)
        self._view.draw_inventory_hud(self._model.inventory)

        if self._model.state == GameState.ONGOING:
            self._view.draw_active_powerup_indicator(self._model.active_powerup, self._model.powerup_ticks_left)
            
        if self._model.state in (GameState.ONGOING, GameState.PAUSED):
            self._view.draw_pause_button(self._model.state == GameState.PAUSED)
        
        if self._model.state == GameState.ROUND_PENDING:
            if self._tower_menu_open and self._selected_tower:
                r, c = self._selected_tower
                if self._model.grid[r][c] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                    curr_lvl = self._model.tower_levels.get((r, c), 0)
                    self._view.draw_tower_menu(r, c, curr_lvl, self._model.total_exp)
                    
            if self._pending_tower_cell:
                r, c = self._pending_tower_cell
                self._view.draw_place_confirm(r, c, self._model.total_exp)

        if self._model.state == GameState.SHOP:
            self._view.draw_shop(self._model.coins, self._model.inventory)
            return None

        if self._model.state == GameState.INVENTORY:
            self._view.draw_inventory_detail(self._model.inventory, self._model.active_powerup)
            return None
        
        if self._model.state == GameState.CONFIRM_RESET:
            self._view.draw_confirm_reset()

        if self._model.state == GameState.CONFIRM_MENU:
            self._view.draw_confirm_menu()
            
        if self._model.state == GameState.QUIT_CONFIRM:
            self._view.draw_quit_confirm()
        
        if self._model.state == GameState.NAME_INPUT:
            self._view.draw_name_input(self._model._nickname, self._model.is_high_score)
        elif self._model.state == GameState.NAME_INPUT_DONE:
            self._view.draw_name_input_done(self._model._nickname)

        if self._model.is_game_over and self._model.state not in (GameState.NAME_INPUT, GameState.NAME_INPUT_DONE):
            self._view.draw_game_over(self._model.total_exp, self._model.user_hp)