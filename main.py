# pyright: strict

from model import *
from view import ZumaTowerView
from controller import ZumaTowerController

if __name__ == '__main__':
    # model = Model.get_simple_model()  # logic
    # model = Model.get_simple_random_model()
    model = ZumaTowerModel.get_inf_random_model()
    view = ZumaTowerView(model.SCREEN_HEIGHT, model.SCREEN_WIDTH)
    controller = ZumaTowerController(model, view)
    controller.start_game()
