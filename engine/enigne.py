import random


class Engine:
    def __init__(self, game):
        self.game = game

        self.train_players = []
        self.train_player_pools = []
        self.test_players = []
        self.test_player_pools = []

        game_info = self.game.get_game_info()

        if hasattr(game_info, 'players_number'):
            self._min_players = self._max_players = game_info.players_number
        elif hasattr(game_info, 'min_players_number') and hasattr(game_info, 'max_players_number'):
            self._min_players = game_info.min_players_number
            self._max_players = game_info.max_players_number
        else:
            raise ValueError('Invalid game info: must contain number of players')

    def set_training_players(self, players=(), player_pools=()):
        self._validate_player_list(players, player_pools)

        self.train_players = players
        self.train_player_pools = player_pools

    def set_testing_players(self, players=(), player_pools=()):
        self._validate_player_list(players, player_pools)

        self.test_players = players
        self.test_player_pools = player_pools

    def train(self, iterations, on_run_complete=None, on_game_complete=None, on_round_complete=None):
        self._run(iterations, True, on_run_complete, on_game_complete, on_round_complete)

    def test(self, iterations, on_run_complete=None, on_game_complete=None, on_round_complete=None):
        self._run(iterations, False, on_run_complete, on_game_complete, on_round_complete)

    def _run(self, iterations, is_train, on_run_complete, on_game_complete, on_round_complete):
        players_list = self.train_players if is_train else self.test_players
        pools_list = self.train_player_pools if is_train else self.test_player_pools

        results_by_players = {player: [] for player in players_list}
        results_by_pools = {pool: [] for pool in pools_list}
        for i in range(iterations):

            for pool in pools_list:
                pool.prepare_new_game()

            players = self._prepare_player_list(players_list, pools_list)

            for player in players:
                player.prepare_new_game()

            self.game.prepare_new_game(players)

            while not self.game.is_game_over():
                for player in players:
                    player.set_current_view(self.game.get_player_view(player))

                self.game.set_players_moves(
                    {player: player.get_next_move() for player in self.game.get_current_players()})

                if on_round_complete:
                    on_round_complete(self.game, players)

            # register results
            result_by_player = {}
            results_by_pool = {}
            for player in players:
                pool = self._pools_by_player[player]
                if pool is None:
                    result_by_player[player] = self.game.get_game_result(player)
                else:
                    if pool not in result_by_player:
                        results_by_pool[pool] = [self.game.get_game_result(player)]
                    else:
                        results_by_pool[pool].append(self.game.get_game_result(player))

            for player, result in zip(result_by_player.keys(), result_by_player.values()):
                results_by_players[player].append(result)
            for pool, results in zip(results_by_pool.keys(), results_by_pool.values()):
                results_by_pools[pool].append(results)

            # finish round
            if on_game_complete:
                on_game_complete(i, self.game, results_by_players, self._pools_by_player)

            results_by_pools_by_players = {}
            for player in players:
                pool = self._pools_by_player[player]
                player.set_current_view(self.game.get_player_view(player))
                if pool is not None:
                    if pool in results_by_pools_by_players:
                        results_by_pools_by_players[pool][player] = self.game.get_game_result(player)
                    else:
                        results_by_pools_by_players[pool] = {player: self.game.get_game_result(player)}

            if is_train:
                for pool, results in zip(results_by_pools_by_players.keys(), results_by_pools_by_players.values()):
                    pool.train_on_game_over(results_by_pools_by_players[pool])

        if on_run_complete:
            on_run_complete(results_by_players, results_by_pools)

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

        self._pools_by_player = {}

        for player in players_list:
            self._pools_by_player[player] = None

        non_empty_pools = set(pools_list)

        per_pool = 1
        while non_empty_pools:
            new_non_empty_pools = set()

            for pool in non_empty_pools:
                player = pool.get_player()
                self._pools_by_player[player] = pool
                players.append(player)

                if len(players) == self._max_players:
                    return players

                if pool.max_count() > per_pool:
                    new_non_empty_pools.add(pool)

            non_empty_pools = new_non_empty_pools
            per_pool += 1

        return players
