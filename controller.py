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
 
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._model.shoot(pyxel.mouse_x, pyxel.mouse_y)
 
    def draw(self) -> None:
        self._view.draw()