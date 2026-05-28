# pyright: strict
import json
from random import Random

from model import ZumaTowerModel, SimpleGameOverCondition  
from view import ZumaTowerView
from controller import ZumaTowerController
from data import Color                                     
from enemies import NormalEnemy

def load_settings() -> dict[str, int]:
    with open("settings.json", "r") as file:
        return json.load(file)

if __name__ == '__main__':
    config = load_settings()
    
    rng = Random()
    phase2_colors = [Color.RED, Color.BLUE]
    
    enemies = [
        NormalEnemy.standard(rng.choice(phase2_colors)) 
        for _ in range(config["enemies_per_round"])
    ]
    
    model = ZumaTowerModel(
        enemies=enemies,
        user_hp=config["player_lives"],
        max_rounds=2,
        game_over_condition=SimpleGameOverCondition(),
        rng=rng
    )
    
    view = ZumaTowerView(model)
    controller = ZumaTowerController(model, view)
    controller.start_game()