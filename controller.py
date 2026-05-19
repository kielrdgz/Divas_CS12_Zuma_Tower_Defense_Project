#pyright: strict

from __future__ import annotations
import pyxel
from view import View, PATH_Y, ENEMY_RADIUS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model import ZumaTowerModel


class Controller:
    def __init__(self, model: ZumaTowerModel, view: View):
        self._model = model
        self._view = view

    def start_game(self) -> None:
        pyxel.run(self._update, self._draw)

    def _update(self) -> None:
        if self._model.is_game_over:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._handle_shoot()

        self._model.tick()

    def _draw(self) -> None:
        self._view.draw(self._model)

    def _handle_shoot(self) -> None:
        shooter_x = self._model.width // 2

        for i, e in enumerate(self._model.enemy_info):
            if e._status.value == "ALIVE":
                if abs(e._x - shooter_x) <= ENEMY_RADIUS:
                    self._model.shoot(i)
                    breaks