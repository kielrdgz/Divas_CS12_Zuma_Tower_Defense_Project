# pyright: strict

from model import *
from view import ZumaTowerView
from controller import ZumaTowerController

if __name__ == '__main__':
    # model = Model.get_simple_model()  # logic
    # model = Model.get_simple_random_model()
    model = ZumaTowerModel.get_phase1_model()
    view = ZumaTowerView(model)
    controller = ZumaTowerController(model, view)
    controller.start_game()