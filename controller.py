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
        # check this first; quitting logic
        if pyxel.btnp(pyxel.KEY_Q):
            if self._model.state not in (GameState.ONGOING, GameState.QUIT_CONFIRM, GameState.GAMEOVER):
                self._model.set_state(GameState.QUIT_CONFIRM)
                return None
            
        if self._model.state == GameState.QUIT_CONFIRM:
            if pyxel.btnp(pyxel.KEY_Y):
                pyxel.quit()
            elif pyxel.btnp(pyxel.KEY_N):
                self._model.resume_from_quit_confirm()
            return None
        
        # check if game over    
        if self._model.is_game_over:
            return None
        
        # pause
        if pyxel.btnp(pyxel.KEY_P):
            if self._model.state == GameState.ONGOING:
                self._model.set_state(GameState.PAUSED)
            elif self._model.state == GameState.PAUSED:
                self._model.resume()

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_pause_clicked():
            if self._model.state == GameState.ONGOING:
                self._model.set_state(GameState.PAUSED)
                return None
            elif self._model.state == GameState.PAUSED:
                self._model.resume()
                return None

        # state
        if self._model.state == GameState.MENU:
            if pyxel.btnp(pyxel.KEY_C):
                self._model.set_game_mode(GameMode.CAMPAIGN)
                self._model.start_round_one()
                # wait ccheck pa kung kailangan pa to pero parang inde na
                # self._model.set_state(GameState.ROUND_PENDING)
                # self._model.bullets.clear()
                # self._model.enemies.clear()
            elif pyxel.btnp(pyxel.KEY_E):
                self._model.set_game_mode(GameMode.ENDLESS)
                self._model.start_round_one()
            elif pyxel.btnp(pyxel.KEY_L):
                self._model.set_state(GameState.LEADERBOARD)
            return None

        elif self._model.state == GameState.LEADERBOARD:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.set_state(GameState.MENU)
            return None

        elif self._model.state == GameState.PAUSED:
            if pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_SPACE): # continues
                self._model.resume()
            elif pyxel.btnp(pyxel.KEY_M): # resets and goes to menu
                self._model.reset_entire_model() 
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
            
            # active = any(e.status == 1 for e in self._model.enemies)
            # if not active and len(self._model.enemies) > 0:
            #     self._model.bullets.clear()
            #     self._model.enemies.clear()
            #     self._model.set_state(GameState.ROUND_PENDING)

        elif self._model.state == GameState.GAMEOVER:
            if pyxel.btnp(pyxel.KEY_M):
                self._model.reset_entire_model()
            elif pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            return None
                
        elif self._model.state == GameState.ROUND_PENDING:
            # navigation
            if pyxel.btnp(pyxel.KEY_Q):  # quit
                self._model.reset_entire_model()
                return None

            if pyxel.btnp(pyxel.KEY_M):
                self._model.set_state(GameState.MENU)
                return None
        
            # if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self._is_pause_clicked() or pyxel.btnp(pyxel.KEY_P):
            #     return None

            # start new round
            if pyxel.btnp(pyxel.KEY_SPACE): # resets
                self._model.start_next_round()
                self._selected_tower = None
                self._tower_menu_open = False
                self._pending_tower_cell = None
                return None

            # grid interaction
            col = pyxel.mouse_x // CELL_SIZE
            row = pyxel.mouse_y // CELL_SIZE
            
            if 0 <= row < self._model.rows and 0 <= col < self._model.cols:
                
                # remove tower (right click)
                if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                    if self._model.grid[row][col] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                        self._model.grid[row][col] = CellType.EMPTY # clear cell
                        self._model._total_exp += 5                 # refund some EXP points
                        if (row, col) in self._model._tower_directions:
                            del self._model._tower_directions[(row, col)]
                        if self._selected_tower == (row, col):
                            self._selected_tower = None
                
                # select, place, upgrade (left click)
                elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    if self._model.grid[row][col] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                        # select tower to open its menu
                        if self._selected_tower == (row, col):
                            self._tower_menu_open = True  # second click on same tower opens menu
                        else:
                            self._selected_tower = (row, col)  # first click just selects
                            self._tower_menu_open = False
                    elif self._model.grid[row][col] == CellType.EMPTY:
                        # only add a tower if the cell is empty 
                        self._selected_tower = None
                        self._tower_menu_open = False
                        self._pending_tower_cell = (row, col) # ask for confirm first before placing

            # selected a tower to place; for confirmation
            if self._pending_tower_cell:
                if pyxel.btnp(pyxel.KEY_Y):
                    row_p, col_p = self._pending_tower_cell
                    current_direction = self._model.pending_direction
                    self._model.try_place_tower(row_p, col_p)
                    if self._model.grid[row_p][col_p] == CellType.TOWER:
                        self._model._tower_directions[(row_p, col_p)] = current_direction
                        self._selected_tower = (row_p, col_p)
                    self._pending_tower_cell = None
                elif pyxel.btnp(pyxel.KEY_N) or pyxel.btnp(pyxel.KEY_X):
                    self._pending_tower_cell = None

            # tower menu is open
            if self._tower_menu_open and self._selected_tower:
                if pyxel.btnp(pyxel.KEY_U):  # upgrade
                    self._model.try_upgrade_tower(self._selected_tower[0], self._selected_tower[1])
                    self._tower_menu_open = False
                elif pyxel.btnp(pyxel.KEY_R):
                    self._model.try_remove_tower(self._selected_tower[0], self._selected_tower[1])
                    self._tower_menu_open = False
                    self._selected_tower = None
                elif pyxel.btnp(pyxel.KEY_X):  # close without doing anything
                    self._tower_menu_open = False 

            if self._tower_menu_open and self._selected_tower and self._model.grid[self._selected_tower[0]][self._selected_tower[1]] in (CellType.TOWER, CellType.UPGRADED_TOWER):
                # can only change tower's dir when menu is open
                if pyxel.btnp(pyxel.KEY_W): self._model._tower_directions[self._selected_tower] = Direction.UP
                elif pyxel.btnp(pyxel.KEY_S): self._model._tower_directions[self._selected_tower] = Direction.DOWN
                elif pyxel.btnp(pyxel.KEY_A): self._model._tower_directions[self._selected_tower] = Direction.LEFT
                elif pyxel.btnp(pyxel.KEY_D): self._model._tower_directions[self._selected_tower] = Direction.RIGHT
            else:
                # if no tower menu open, wasd sets dir for the next placement of tower
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

        if self._model.state == GameState.QUIT_CONFIRM:
            self._view.draw_quit_confirm()

        if self._model.is_game_over:
            self._view.draw_game_over(self._model.total_exp, self._model.user_hp)

        