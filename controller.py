#pyright: strict

from __future__ import annotations
import pyxel
from model import ZumaTowerModel
from view import ZumaTowerView
from data import CellType, Direction, GameState, CELL_SIZE
    
class ZumaTowerController:
    def __init__(self, model: ZumaTowerModel, view: ZumaTowerView):
        self._model = model
        self._view = view

    def start_game(self) -> None:
        self._view.start_game(self, self) # update, draw

    def update(self) -> None:
        if self._model.is_game_over:
            return
 
        self._model.update()
 
        if self._model.state == GameState.ONGOING:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): # only shoot if round is ongoing
                self._model.shoot(pyxel.mouse_x, pyxel.mouse_y)
                
        elif self._model.state == GameState.ROUND_PENDING:
            if pyxel.btnp(pyxel.KEY_Q): # quit
                pyxel.quit()

            if pyxel.btnp(pyxel.KEY_W): # wasd to set tower shoot direction before placing a tower
                self._model.set_pending_direction(Direction.UP)
            elif pyxel.btnp(pyxel.KEY_S):
                self._model.set_pending_direction(Direction.DOWN)
            elif pyxel.btnp(pyxel.KEY_A):
                self._model.set_pending_direction(Direction.LEFT)
            elif pyxel.btnp(pyxel.KEY_D):
                self._model.set_pending_direction(Direction.RIGHT)

            if pyxel.btnp(pyxel.KEY_SPACE): # space to start next round
                self._model.start_next_round() # resets

            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                col = pyxel.mouse_x // CELL_SIZE
                row = pyxel.mouse_y // CELL_SIZE
                if self._model.grid[row][col] == CellType.TOWER: # click on tower to upgrade
                    self._model.try_upgrade_tower(row, col)
                else:  # click on grid to place tower
                    self._model.try_place_tower(row, col)
 
    def draw(self) -> None:
        self._view.reset_screen()
        self._view.draw_paths(self._model.paths)
        self._view.draw_towers(self._model.rows, self._model.cols, self._model.grid)
        self._view.draw_enemies(self._model.enemies)
        self._view.draw_bullets(self._model.bullets)
        self._view.draw_shooter(self._model.shooter_x, self._model.shooter_y, self._model.bullet_color)
        self._view.draw_hud(self._model.user_hp, self._model.total_exp, self._model.curr_round, self._model.max_rounds, self._model.state, self._model.pending_direction)
        
        if self._model.is_game_over:
            self._view.draw_game_over(self._model.total_exp, self._model.is_game_over)