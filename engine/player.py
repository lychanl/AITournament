class Player:
    def __init__(self):
        self.view = None
        self.name = None

    def set_current_view(self, view):
        self.view = view

    def get_next_move(self):
        raise NotImplementedError

    def train_game_over(self, game_over_result):
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


class ParametrizedPlayer(Player):
    def __init__(self):
        super(ParametrizedPlayer, self).__init__()
        self.session = None

    def get_variable_list(self):
        raise NotImplementedError

    def get_next_move(self):
        raise NotImplementedError
