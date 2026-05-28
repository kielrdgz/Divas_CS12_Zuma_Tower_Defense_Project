#pyright: strict

from __future__ import annotations

import pyxel
from typing import TYPE_CHECKING
from data import Color, PYXEL_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE

if TYPE_CHECKING:
    from model import ZumaTowerModel
    
BULLET_RADIUS = 5
ENEMY_HALF = CELL_SIZE // 2

COL_WHITE = 7
COL_DARK = 1

class ZumaTowerView:
    def __init__(self, model: ZumaTowerModel):
        self._model = model
        
    def start_game(self, update_fn: object, draw_dn: object) -> None:
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Zuma Tower Defense", fps=FPS)
        pyxel.mouse(True)
        pyxel.run(
            getattr(update_fn, "update"),
            getattr(draw_dn, "draw")
        )
        
    def draw(self) -> None:
        pyxel.cls(0)
        m = self._model
        
        self._draw_path()
        self._draw_towers()
        self._draw_enemies()
        self._draw_bullets()
        self._draw_shooter()
        self._draw_hud()
        
        if m.is_game_over:
            self._draw_game_over()
            
    def _draw_path(self) -> None:
        m = self._model
        
        for i in range(len(m._path) - 1):
            x1, y1 = m._path[i]
            x2, y2 = m._path[i+1]
            
            pyxel.line(x1, y1, x2, y2, 5)
        
    def _draw_enemies(self) -> None:
        m = self._model
        for e in m.enemies:
            from data import EnemyStatus
            if e.status != EnemyStatus.ALIVE:
                continue
            if e.x < -CELL_SIZE:
                continue
            col = PYXEL_COLOR[e.color]
            ex = int(e.x)
            ey = int(e.y)
            pyxel.rect(ex - ENEMY_HALF, ey - ENEMY_HALF,
                       ENEMY_HALF * 2, ENEMY_HALF * 2, col)
            pyxel.rectb(ex - ENEMY_HALF, ey - ENEMY_HALF,
                        ENEMY_HALF * 2, ENEMY_HALF * 2, COL_DARK)
 
    def _draw_bullets(self) -> None:
        m = self._model
        for b in m.bullets:
            col = PYXEL_COLOR[b.color]
            pyxel.circ(int(b.x), int(b.y), BULLET_RADIUS, col)
 
    def _draw_shooter(self) -> None:
        m = self._model
        sx = int(m.shooter_x)
        sy = int(m.shooter_y)
        pyxel.tri(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_WHITE)
        pyxel.trib(sx, sy - 10, sx - 7, sy + 5, sx + 7, sy + 5, COL_DARK)
        col = PYXEL_COLOR[m.bullet_color]
        pyxel.circ(sx, sy, 3, col)

    def _draw_towers(self) -> None:
        from data import CellType
        m = self._model
        for r in range(m._rows):
            for c in range(m._cols):
                if m._grid[r][c] == CellType.TOWER:
                    x = c * CELL_SIZE
                    y = r * CELL_SIZE
                    # Draw an orange block for the tower
                    pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, 9)
 
    def _draw_hud(self) -> None:
        m = self._model
        pyxel.text(4, 4,  f"HP:  {m.user_hp}", COL_WHITE)
        pyxel.text(4, 12, f"EXP: {m.total_exp}", COL_WHITE)
        pyxel.text(4, 20, f"Round: {m._curr_round}/{m._max_rounds}", COL_WHITE)
        
        if m.state.value == "ROUNDPENDING":
            pyxel.rect(40, 90, 240, 50, COL_DARK)
            pyxel.text(50, 98, "ROUND 1 COMPLETE!", COL_WHITE)
            pyxel.text(50, 110, "Click grid to place Tower (Cost: 5 EXP)", 9)
            pyxel.text(50, 124, "Press SPACE to start Round 2", 10)
 
    def _draw_game_over(self) -> None:
        m = self._model
        pyxel.rect(60, 90, 200, 60, COL_DARK)
        if m.player_won:
            pyxel.text(100, 100, "YOU WIN!", COL_WHITE)
            pyxel.text(80,  112, f"EXP earned: {m.total_exp}", COL_WHITE)
        else:
            pyxel.text(100, 100, "GAME OVER", 8)
        pyxel.text(80, 128, "Close window to exit.", 13)