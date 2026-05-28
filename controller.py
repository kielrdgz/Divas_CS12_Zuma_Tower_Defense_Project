#pyright: strict

from __future__ import annotations
import pyxel
from view import ZumaTowerView #, ENEMY_RADIUS, PATH_Y
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model import ZumaTowerModel


class ZumaTowerController:
    def __init__(self, model: ZumaTowerModel, view: ZumaTowerView):
        self._model = model
        self._view = view

    def start_game(self) -> None:
        self._view.start_game(self, self)


    def update(self) -> None:
        if self._model.is_game_over:
            return
 
        self._model.update()
 
        if self._model.state.value == "ONGOING":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self._model.shoot(pyxel.mouse_x, pyxel.mouse_y)
                
        elif self._model.state.value == "ROUNDPENDING":
            # Press Space to start Round 2
            if pyxel.btnp(pyxel.KEY_SPACE):
                self._model.start_next_round()
                
            # Click to place a tower
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                from data import CELL_SIZE
                col = pyxel.mouse_x // CELL_SIZE
                row = pyxel.mouse_y // CELL_SIZE
                self._model.try_place_tower(row, col)
 
        self._model.update()
 
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._model.shoot(pyxel.mouse_x, pyxel.mouse_y)
 
    def draw(self) -> None:
        self._view.draw()