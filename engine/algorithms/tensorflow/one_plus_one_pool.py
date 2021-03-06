import tensorflow as tf

from engine.player_pool import PlayerPool
from engine.player import ParametrizedPlayer


class OnePlusOnePlayerPool(PlayerPool):
    def __init__(self, session, player_type,
                 sigma_proportion=1.2,
                 sigma_scaling_interval=10,
                 win_proportion=0.2):
        super(OnePlusOnePlayerPool, self).__init__()
        assert issubclass(player_type, ParametrizedPlayer)

        self._session = session
        self._first_player = player_type()
        self._first_player.session = session
        self._second_player = player_type()
        self._second_player.session = session
        self._best_player = self._first_player
        self.active_players = 0

        self._first_player.set_name("{}: Initial player 1".format(self.get_name()))
        self._second_player.set_name("{}: Initial player 2".format(self.get_name()))

        self._sigma_scaling_interval = sigma_scaling_interval
        self._sigma_scaling_t = 0
        self._win_proportion = win_proportion
        self._new_player_wins = 0

        self.sigma = 1.
        self._sigma_proportion = sigma_proportion
        self._sigma_placeholder = tf.placeholder(tf.float32)

        self._from_first_player_setter = self._create_setter(self._first_player, self._second_player)
        self._from_second_player_setter = self._create_setter(self._second_player, self._first_player)

    def max_count(self):
        return 2

    def get_player(self):
        if self.active_players == 2:
            raise ValueError("Max players number exceeded")

        if self.active_players == 0:
            self.active_players = 1
            return self._best_player

        self.active_players = 2
        if self._best_player is self._first_player:
            return self._second_player
        else:
            return self._first_player

    def train_on_game_over(self, players_results):
        assert self.active_players == len(players_results)

        if self.active_players != 2:
            return

        new_player = self._second_player if self._best_player is self._first_player else self._first_player

        if players_results[self._best_player] <= players_results[new_player]:
            self._new_player_wins += 1
            self._best_player = new_player

        setter = self._from_first_player_setter if self._best_player is self._first_player else self._from_second_player_setter
        self._session.run(setter, {self._sigma_placeholder: self.sigma})

        self._best_player.set_name("{}: Best player".format(self.name))
        if self._best_player is self._first_player:
            self._second_player.set_name("{}: New player".format(self.name))
        else:
            self._first_player.set_name("{}: New player".format(self.name))

        self._scale_sigma()

    def prepare_new_game(self):
        self.active_players = 0

    def _scale_sigma(self):
        self._sigma_scaling_t += 1
        if self._sigma_scaling_t == self._sigma_scaling_interval:
            win_proportion = self._new_player_wins / self._sigma_scaling_interval

            if win_proportion > self._win_proportion:
                self.sigma *= self._sigma_proportion
            else:
                self.sigma /= self._sigma_proportion

            self._sigma_scaling_t = 0
            self._new_player_wins = 0

    def _create_setter(self, source, dest):
        return tf.group([
            tf.assign(dst, src + tf.random_normal(src.get_shape(), stddev=self._sigma_placeholder))
            for src, dst in zip(source.get_variable_list(), dest.get_variable_list())
        ])

