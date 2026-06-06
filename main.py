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
    
    paths = [
        [  # path 1
            ZumaTowerView.cell_center(row=2, col=5), 
            ZumaTowerView.cell_center(row=10, col=5), 
            ZumaTowerView.cell_center(row=10, col=15),
        ],
        [  # path 2
            ZumaTowerView.cell_center(row=7, col=10),
            ZumaTowerView.cell_center(row=3, col=10),
        ],
    ]
    
    
    
    tunnels = {
        0: [
            (float(5 * CELL_SIZE), float(5 * CELL_SIZE), float(1 * CELL_SIZE), float(3 * CELL_SIZE)),   
            (float(10 * CELL_SIZE), float(10 * CELL_SIZE), float(4 * CELL_SIZE), float(1 * CELL_SIZE))
        ],
        1: []
    }

    model = ZumaTowerModel(
        enemies=[],
        user_hp=config.get("player_lives", 3),  # user_hp=config["player_lives"],
        max_rounds=rounds,
        game_over_condition=SimpleGameOverCondition(),
        rng=rng,
        paths=paths,
        tunnels=tunnels, 
        popupplan=SimpleEnemyPopupPlan(),
        settings_enemies=config.get("enemies_per_round")
    )

    model.set_state(GameState.MENU)
    
    view = ZumaTowerView()
    controller = ZumaTowerController(model, view)
    controller.start_game()