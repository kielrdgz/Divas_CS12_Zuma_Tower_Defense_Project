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

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._handle_shoot()

    def draw(self) -> None:
        pyxel.cls(0)
        self._view.draw_player()
        alive_enemies = [e for e in self._model.enemies if self._model.enemies]
        self._view.draw_enemies(e)

    def _handle_shoot(self) -> None:
        shooter_x = self._model.width // 2

        for i, e in enumerate(self._model.enemy_info):
            if e._status.value == "ALIVE":
                if abs(e._x - shooter_x) <= ENEMY_RADIUS:
                    self._model.shoot(i)
                    break