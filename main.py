# pyright: strict

from model import *
from view import View
from controller import Controller


if __name__ == '__main__':
    # model = Model.get_simple_model()  # logic
    # model = Model.get_simple_random_model()
    model = Model.get_inf_random_model()

    view = View(200, 200)  # what the user sees
    controller = Controller(model, view)  # glues model & view

    controller.start_game()
