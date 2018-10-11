class Player:
    def __init__(self):
        self.id = None
        self.view = None

    def set_player_id(self, id_):
        self.id = id_

    def set_current_view(self, view):
        self.view = view

    def get_next_move(self):
        raise NotImplementedError

    def train_game_over(self, game_over_result):
        pass

    def prepare_new_game(self):
        pass

