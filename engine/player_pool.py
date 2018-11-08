class PlayerPool:
    def __init__(self):
        self.current_players = None

    def max_count(self):
        raise NotImplementedError

    def get_player(self):
        raise NotImplementedError

    def train_on_game_over(self, players_results):
        pass

    def prepare_new_game(self):
        pass

