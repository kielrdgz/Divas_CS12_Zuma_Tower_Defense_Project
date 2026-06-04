# pyright: strict
from data import FPS, Direction

class Tower:
    COST: int = 5
    _cost: int = 5
    
    def __init__(self, x: float, y: float, direction: Direction) -> None:
        self._cost: int = 5
        self._x: float = x
        self._y: float = y
        self._cooldown_max: int = FPS  # one bullet per second
        self._current_cooldown: int = 0
        self._direction: Direction = direction
        
    def set_direction(self, direction: Direction) -> None:
        self._direction = direction
        
    @property
    def x(self) -> float:
        return self._x
        
    @property
    def y(self) -> float:
        return self._y
    
    @property
    def is_upgraded(self) -> bool:
        return False
    
    @property
    def direction(self) -> Direction:
        return self._direction
        
    def can_shoot(self) -> bool:
        return self._current_cooldown <= 0
        
    def update_cooldown(self) -> None:
        if self._current_cooldown > 0:
            self._current_cooldown -= 1
            
    def reset_cooldown(self) -> None:
        self._current_cooldown = self._cooldown_max

class UpgradedTower(Tower):
    UPGRADE_COST: int = 5
    _cost: int = 5

    def __init__(self, x: float, y: float, direction: Direction) -> None:
        super().__init__(x, y, direction)
        self._cost: int = 5
        self._cooldown_max = FPS

    @property
    def is_upgraded(self) -> bool:
        return True