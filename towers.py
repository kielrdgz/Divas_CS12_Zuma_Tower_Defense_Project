# pyright: strict
from __future__ import annotations
from data import FPS, Direction

COUNT = 3
SPACING = 9   
COOLDOWN = 30 

class Tower:
    COST: int = 5
    UPGRADE_COST: int = 10
    upgrade_level = 0
    
    def __init__(self, r: int, c: int, direction: Direction) -> None:
        self.r: int = r
        self.c: int = c
        self._direction: Direction = direction
        
        # Calculate pixel coordinates dynamically based on grid cells
        # This keeps bullet spawning logic fully intact!
        self._x: float = (c * 16) + 8  # Assuming CELL_SIZE = 16
        self._y: float = (r * 16) + 8
        
        self._cooldown_max: int = FPS
        self._current_cooldown: int = 0
        
    def set_direction(self, direction: Direction) -> None:
        self._direction = direction
        
    @property
    def x(self) -> float: 
        return self._x
        
    @property
    def y(self) -> float: 
        return self._y
        
    @property
    def direction(self) -> Direction: 
        return self._direction
        
    @property
    def is_upgraded(self) -> bool: 
        return False
        
    @property
    def upgrade_level(self) -> int: 
        return 0
        
    def can_shoot(self) -> bool:
        return self._current_cooldown <= 0
        
    def update_cooldown(self) -> None:
        if self._current_cooldown > 0:
            self._current_cooldown -= 1
            
    def reset_cooldown(self) -> None:
        self._current_cooldown = self._cooldown_max
        
    def bullets_this_tick(self) -> int:
        return 1 if self.can_shoot() else 0
        
    @property
    def double_shot(self) -> bool:
        return False


class UpgradedTower(Tower):
    COST: int = 10
    UPGRADE_COST: int = 20
    upgrade_level = 1
    
    def __init__(self, x: float, y: float, direction: Direction) -> None:
        super().__init__(x, y, direction)
        self._burst_shots_left: int = 0
        self._burst_cooldown: int = 0
        self._shot_spacing: int = 0
        
    @property
    def is_upgraded(self) -> bool: 
        return True
        
    @property
    def upgrade_level(self) -> int: 
        return 1
        
    def update_cooldown(self) -> None:
        if self._burst_shots_left > 0:
            if self._shot_spacing > 0:
                self._shot_spacing -= 1
        else:
            if self._burst_cooldown > 0:
                self._burst_cooldown -= 1
                
    def can_shoot(self) -> bool:
        if self._burst_shots_left == 0 and self._burst_cooldown == 0:
            self._burst_shots_left = COUNT
            self._shot_spacing = 0
            return True
            
        if self._burst_shots_left > 0 and self._shot_spacing == 0:
            return True
            
        return False
        
    def reset_cooldown(self) -> None:
        self._burst_shots_left -= 1
        if self._burst_shots_left > 0:
            self._shot_spacing = SPACING  
        else:
            self._burst_cooldown = COOLDOWN 


class UpgradedTower2(UpgradedTower):
    COST: int = 20
    UPGRADE_COST: int = 0  # max reached
    upgrade_level = 2
    
    def __init__(self, x: float, y: float, direction: Direction) -> None:
        super().__init__(x, y, direction)
        
    @property
    def is_upgraded(self) -> bool: 
        return True
        
    @property
    def upgrade_level(self) -> int: 
        return 2
        
    @property
    def double_shot(self) -> bool: 
        return True  