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
