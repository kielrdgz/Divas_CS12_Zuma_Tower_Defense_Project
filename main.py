# pyright: strict
import json
from random import Random
from model import ZumaTowerModel, SimpleGameOverCondition  
from view import ZumaTowerView
from controller import ZumaTowerController
from data import *                     
from enemies import NormalEnemy, Enemy

def load_settings() -> dict[str, int]:
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"enemies_per_round": 8,
                "player_lives": 10,
                }

if __name__ == '__main__':
    config = load_settings()
    rng = Random()
   
    # colors = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN] 
    colors = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.BLUE, Color.VIOLET]
    rounds = 12
    
    enemies: list[Enemy] = [
        NormalEnemy.standard(rng.choice(colors)) 
        for _ in range(config["enemies_per_round"])
    ]
    
    paths = [
        [  # path 1
            (80.0,  40.0), 
            (80.0, 160.0), 
            (240.0, 160.0),
        ],
        [  # path 2
            (160.0, 120.0),
            (160.0,  60.0),
        ],
    ]
    
    
    
    tunnels = {
        0: [
            (72.0, 80.0, 16.0, 48.0),   
            (160.0, 152.0, 64.0, 16.0) 
        ],
        1: []
    }

    model = ZumaTowerModel(
        enemies=enemies,
        user_hp=config["player_lives"],
        max_rounds=rounds,
        game_over_condition=SimpleGameOverCondition(),
        rng=rng,
        paths=paths,
        tunnels=tunnels, 
        popupplan=SimpleEnemyPopupPlan()
    )

    model.set_state(GameState.MENU)
    
    view = ZumaTowerView()
    controller = ZumaTowerController(model, view)
    controller.start_game()