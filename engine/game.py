class Game:
    def __init__(self):
        self._players = None

    def prepare_new_game(self, players):
        self._players = players

        self._prepare_new_game()

    def get_players(self):
        return self._players

    def _prepare_new_game(self):
        raise NotImplementedError

    def get_game_info(self):
        """ Returned value must contain at least one of:
            players_number - integer
            max_players_number and min_players_number - integer

            Simple implementations:
                ConstPlayersNGameInfo
                RangePlayersNGameInfo
        """
        raise NotImplementedError

    def get_player_view(self, player):
        raise NotImplementedError

    def get_current_players(self):
        raise NotImplementedError

    def set_players_moves(self, moves):
        """
        Args:
            moves - dictionary with players as keys
        """
        raise NotImplementedError

    def is_game_over(self):
        raise NotImplementedError

    def get_game_result(self, player):
        """ Must be comparable if is to be used with some player pools
        """
        raise NotImplementedError

    def __str__(self):
        return "{}.{}".format(type(self).__module__, type(self).__name__)


class ConstPlayersNGameInfo:
    def __init__(self, n):
        self.players_number = n


class RangePlayersNGameInfo:
    def __init__(self, min_, max_):
        self.min_players_number = min_
        self.max_players_number = max_


class FiniteTurnGameLogic:
    """ Class for games that are:
        - not random,
        - turn-based (no concurrent moves) and
        - have finite moves set for each state
        - every player has full knowledge about game state
    """

    def get_current_player(self, game_view):
        """
        returns: player that is supposed to make next move
        """
        raise NotImplementedError

    def list_moves(self, game_view):
        """
        returns: list of moves available to current player
        """
        raise NotImplementedError

    def is_view_terminal(self, game_view):
        """
        returns: if a view is a terminal state for the game
        """
        raise NotImplementedError

    def apply_move(self, game_view, move):
        """ Calculates new view assuming that current player made given move

        args:
            game_view: current view
            move: move selected by current player

        returns: new game view after applying move
        """
        raise NotImplementedError

    def evaluate_view(self, view, viewpoint_player):
        """ Evaluates view (returns comparable object) from point of view of given player
        (with expectation that the higher is the evaluation the better is the situation)
        """
        raise NotImplementedError
