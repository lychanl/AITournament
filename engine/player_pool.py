class PlayerPool:
    def __init__(self):
        self.current_players = None
        self.name = None

    def max_count(self):
        raise NotImplementedError

    def get_player(self):
        raise NotImplementedError

    def train_on_game_over(self, players_results):
        pass

    def prepare_new_game(self):
        pass

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def __str__(self):
        if self.name is not None:
            return "{}: {}.{}".format(self.name, type(self).__module__, type(self).__name__)
        else:
            return "Instance of {}.{}".format(type(self).__module__, type(self).__name__)
