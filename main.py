# pyright: strict
import json
from random import Random
from model import ZumaTowerModel, SimpleGameOverCondition  
from view import ZumaTowerView
from controller import ZumaTowerController
from data import Color                                     
from enemies import NormalEnemy, Enemy

def load_settings() -> dict[str, int]:
    with open("settings.json", "r") as file:
        return json.load(file)

if __name__ == '__main__':
    config = load_settings()
    
    rng = Random()
    colors = [Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN] # phase 4 colors; change when doing next phase
    rounds = 4 # phase 4 rounds
    
    enemies: list[Enemy] = [
        NormalEnemy.standard(rng.choice(colors)) 
        for _ in range(config["enemies_per_round"])
    ]
    
    # change pa depending on path 
    paths = [
        [  # path 1
            (80.0,  40.0), # start
            (80.0, 160.0), # turn (x, y)
            (240.0, 160.0),
        ],
        [  # path 2
            (160.0, 120.0),
            (160.0,  60.0),
        ],
    ]

    model = ZumaTowerModel(
        enemies=enemies,
        user_hp=config["player_lives"],
        max_rounds=rounds,
        game_over_condition=SimpleGameOverCondition(),
        rng=rng,
        paths=paths,
    )
    
    view = ZumaTowerView()
    controller = ZumaTowerController(model, view)
    controller.start_game()