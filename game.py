class Game:
    def __init__(self):
        self._player_ids = {}
        self._players = None

    def prepare_new_game(self, players):
        self._players = players

        player_id = 0
        for player in players:
            self._player_ids[player] = player_id
            player.set_player_id(player_id)
            player_id += 1

    """ Returned value must contain at least one of:
        players_number - integer
        max_players_number and min_players_number - integer
    """
    def get_game_info(self):
        raise NotImplementedError

    def get_player_view(self, player):
        raise NotImplementedError

    def get_current_players(self):
        raise NotImplementedError

    def get_player_id(self, player):
        return self._player_ids[player]

    """ 
    Args:
        moves - dictionary with players as keys
    """
    def set_players_moves(self, moves):
        raise NotImplementedError

    def is_game_over(self):
        raise NotImplementedError

    """ Must be comparable if is to be used with some player pools
    """
    def get_game_result(self, player):
        raise NotImplementedError


class FiniteTurnGameLogic:
    """ Class for games that are:
        - not random,
        - turn-based (no concurrent moves) and
        - have finite moves set for each state
        - every player has full knowledge about game state
    """

    """
    returns: player that is supposed to make next move
    """
    def get_current_player(self, game_view):
        raise NotImplementedError

    """
    returns: list of moves available to current player 
    """
    def list_moves(self, game_view):
        raise NotImplementedError

    """
    returns: if a view is a terminal state for the game
    """
    def is_view_terminal(self, game_view):
        raise NotImplementedError

    """ Calculates new view assuming that current player made given move
    
    args:
        game_view: current view
        move: move selected by current player
        
    returns: new game view after applying move
    """
    def apply_move(self, game_view, move):
        raise NotImplementedError

    """ Evaluates view (returns comparable object) from point of view of given player
    (with expectation that the higher is the evaluation the better is the situation)
    """
    def evaluate_view(self, view, viewpoint_player):
        raise NotImplementedError

