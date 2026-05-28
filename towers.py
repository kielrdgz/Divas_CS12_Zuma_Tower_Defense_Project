# pyright: strict
from data import FPS

class Tower:
    COST: int = 5
    
    def __init__(self, x: float, y: float) -> None:
        self._x: float = x
        self._y: float = y
        
        # Fires 1 bullet per second
        self._cooldown_max: int = FPS
        self._current_cooldown: int = 0
        
    @property
    def x(self) -> float:
        return self._x
        
    @property
    def y(self) -> float:
        return self._y
        
    def can_shoot(self) -> bool:
        return self._current_cooldown <= 0
        
    def update_cooldown(self) -> None:
        if self._current_cooldown > 0:
            self._current_cooldown -= 1
            
    def reset_cooldown(self) -> None:
        self._current_cooldown = self._cooldown_max