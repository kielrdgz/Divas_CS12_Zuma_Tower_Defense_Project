#pyright: strict

from __future__ import annotations
from abc import ABC, abstractmethod
from data import Color, EnemyStatus, EnemyType
import pyxel

class ZumaTowerView:
    def __init__(self, width, height):
        self._width = width
        self._height = height
    
    def start_game(self, update_handler, draw_handler) -> None:
        pyxel.init(self.width, self.height, title="Zuma Tower")
        pyxel.mouse(True)
        # pyxel.load([wtvr sprite file])
        pyxel.run(update_handler.update, draw_handler.draw)

    # for testing muna yung circles but will replace with sprites when done
    def draw_player(self):
        pyxel.circ(100, 100, 5, 10)

    def draw_enemies(self, enemies: Sequence[Enemy]):
        for enemy in enemies:
            pyxel.rect(enemy.x, enemy.y, 10, 10, enemy.color)
