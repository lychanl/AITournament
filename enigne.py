import random


class Engine:
    def __init__(self, game):
        self.game = game

        self.train_players = ()
        self.train_player_pools = ()
        self.test_players = ()
        self.test_player_pools = ()

        game_info = self.game.get_game_info()

        if hasattr(game_info, 'players_number'):
            self._min_players = self._max_players = game_info.players_number
        elif hasattr(game_info, 'min_players_number') and hasattr(game_info, 'max_players_number'):
            self._min_players = game_info.min_players_number
            self._max_players = game_info.max_players_number
        else:
            raise AttributeError('Invalid game info: must contain number of players')

    def set_training_players(self, players=(), player_pools=()):
        self._validate_player_list(players, player_pools)

        self.players = players
        self.player_pools = player_pools

    def set_testing_players(self, players=(), player_pools=()):
        self._validate_player_list(players, player_pools)

        self.test_players = players
        self.test_player_pools = player_pools

    """ Game players will be taken from set list 
    and remaining will be filled with players from pools,
    according to the number of game players.
    From every pool there will be taken equal number of players,
    up to maximum generated from the pool, at least one from each
    
    Args:
        iterations - number of iterations (full games) of training
        on_game_complete - None or function that accepts integer, game and a list of players 
                           and returns truthy or falsey value - if training should continue  
    """
    def train(self, iterations, on_iteration_complete=None):
        for i in range(iterations):
            players = self._prepare_player_list(self.train_players, self.train_player_pools)
            random.shuffle(players)

            self.game.prepare_new_game(players)
            for player in players:
                player.prepare_new_game()
            for pool in self.train_player_pools:
                pool.prepare_new_game()

            while not self.game.is_game_over():
                for player in players:
                    player.set_current_view(self.game.get_player_view(player))

                self.game.set_players_moves({player: player.get_next_move() for player in players})

            for player in players:
                player.set_current_view(self.game.get_player_view(player))
                player.game_over(self.game.get_game_result(player))

            for pool, pool_players in self._pool_players:
                pool.game_over({player: self.game.get_game_result(player) for player in pool_players})

            if on_iteration_complete:
                if not on_iteration_complete(i, self.game, players):
                    break

    """ Game players will be taken from set list 
    and remaining will be filled with players from pools,
    according to the number of game players.
    From every pool there will be taken equal number of players,
    up to maximum generated from the pool
    
    args:
        iterations - number of iterations (full games) of training
        on_round_complete - None or function that accepts game and a list of players
        on_game_complete - None or function that accepts game and a list of players
    """
    def test(self, on_round_complete=None, on_game_complete=None):
        players = self._prepare_player_list(self.test_players, self.test_player_pools)
        random.shuffle(players)

        self.game.prepare_new_game(players)
        for player in players:
            player.prepare_new_game()
        for pool in self.test_player_pools:
            pool.prepare_new_game()

        while not self.game.is_game_over():
            for player in players:
                player.set_current_view(self.game.get_player_view(player))

            self.game.set_players_moves({player: player.get_next_move() for player in players})

            if on_round_complete:
                on_round_complete(self.game, players)

        if on_game_complete:
            on_game_complete(self.game, players)

    def _validate_player_list(self, players, player_pools):
        if not len(players) + len(player_pools):
            raise ValueError('players or player_pools must not be empty')
        if len(players) + len(player_pools) > self._max_players:
            raise ValueError('too large player number')
        if len(players) + sum([pool.max_count() for pool in player_pools]) < self._min_players:
            raise ValueError('not enough available players')
        for pool in player_pools:
            if pool.max_count() < 1:
                raise ValueError('Player pool must allow for at least one player')

    def _prepare_player_list(self, players_list, pools_list):
        players = [] + players_list

        self._pool_players = {}

        for pool in pools_list:
            self._pool_players[pool] = []

        non_empty_pools = set(pools_list)

        while not non_empty_pools:
            new_non_empty_pools = set()
            for pool in non_empty_pools:

                player = pool.get_player()
                self._pool_players[pool].append(player)
                players.append(player)

                if len(players) == self._max_players:
                    return players

                if pool.max_count() > len(self._pool_players[pool]):
                    new_non_empty_pools.add(pool)
            non_empty_pools = new_non_empty_pools

        return players
