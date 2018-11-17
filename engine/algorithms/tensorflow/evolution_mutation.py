import random
import tensorflow as tf

from engine.player_pool import PlayerPool
from engine.player import ParametrizedPlayer


class EvolutionWithMutationPlayerPool(PlayerPool):
    def __init__(self, session, player_type,
                 stddev,
                 pool_size,
                 tournament_size,
                 tournament_1_on_1):
        super(EvolutionWithMutationPlayerPool, self).__init__()
        assert issubclass(player_type, ParametrizedPlayer)

        self._session = session

        self._winners = None
        self._tournament_size = tournament_size
        self._current_tournament = None
        self._current_tournament_player = None
        self._current_tournament_added_player = None
        self._left_players = []

        self._tournament_1_on_1 = tournament_1_on_1

        self._players = [player_type() for _ in range(pool_size)]
        for player in self._players:
            player.session = session

        self._setters = self._create_setters(stddev)
        self._in_game = 0
        self._unselected_for_tournament = list(self._players)

    def _reset_tournament(self):
        self._current_tournament = None
        self._current_tournament_player = None
        self._current_tournament_added_player = None
        self._left_players = []
        self._unselected_for_tournament = list(self._players)

    def _create_setters(self, stddev):
        setters = {}

        for player in self._players:
            from_player = {}
            for target_player in self._players:
                from_player[target_player] = self._create_setter(player, target_player, stddev)
            setters[player] = from_player

        return setters

    def _create_setter(self, from_player, to_player, stddev):
        ops = [
            tf.assign(var_to, var_from + tf.random_normal(var_from.get_shape(), stddev=stddev))
            for var_from, var_to in zip(from_player.get_variable_list(), to_player.get_variable_list())
        ]

        return tf.group(ops)

    def max_count(self):
        return 2 if self._tournament_1_on_1 else self._tournament_size

    def get_player(self):
        self._in_game += 1
        if not self._tournament_1_on_1:
            return random.choice(self._players)

        if self._in_game == 1:
            if self._current_tournament_added_player is None:
                self._current_tournament_added_player = random.choice(self._unselected_for_tournament)
                self._unselected_for_tournament.remove(self._current_tournament_added_player)
            return self._current_tournament_added_player

        if self._current_tournament_player is None:
            self._current_tournament_player = random.choice(self._unselected_for_tournament)
            self._unselected_for_tournament.remove(self._current_tournament_player)

        return self._current_tournament_player

    def train_on_game_over(self, players_results):
        assert len(players_results) == self.max_count()
        if not self._tournament_1_on_1:
            winner = max(zip(players_results.keys(), players_results.values()), key=lambda kv: kv[1])[0]
            if self._winners is None:
                self._winners = [winner]
            else:
                self._winners.append(winner)

        else:
            if self._current_tournament is None:
                self._current_tournament = {player: 0 for player in players_results.keys()}
            if self._current_tournament_added_player not in self._current_tournament:
                self._current_tournament[self._current_tournament_added_player] = 0

            res_1 = players_results[self._current_tournament_added_player]
            res_2 = players_results[self._current_tournament_player]

            if res_1 > res_2:
                self._current_tournament[self._current_tournament_added_player] += 3
            elif res_2 > res_1:
                self._current_tournament[self._current_tournament_player] += 3
            else:
                self._current_tournament[self._current_tournament_added_player] += 1
                self._current_tournament[self._current_tournament_player] += 1

            if self._left_players:  # select next player
                self._current_tournament_player = self._left_players.pop()
            else:
                if self._tournament_size > len(self._current_tournament):
                    self._left_players = list(self._current_tournament.keys())
                    self._current_tournament_player = self._left_players.pop()
                    self._current_tournament_added_player = None
                else:
                    winner = max(
                        zip(self._current_tournament.keys(), self._current_tournament.values()),
                        key=lambda kv: kv[1]
                    )[0]
                    if self._winners is None:
                        self._winners = [winner]
                    else:
                        self._winners.append(winner)

                    self._reset_tournament()

        if self._winners and len(self._winners) == len(self._players):
            self._next_generation()

    def _next_generation(self):
        to_generate = self._players

        while len(self._winners) > 0:
            next_to_generate = []
            for p in to_generate:
                if p not in self._winners:
                    self._session.run(self._setters[self._winners.pop()][p])
                elif self._winners.count(p) == 1:
                    self._session.run(self._setters[p][p])
                    self._winners = [winner for winner in self._winners if winner is not p]
                else:
                    next_to_generate.append(p)
            to_generate = next_to_generate

    def prepare_new_game(self):
        self._in_game = 0
