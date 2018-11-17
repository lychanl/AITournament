import tensorflow as tf

from engine.algorithms.tensorflow.one_plus_one_pool import OnePlusOnePlayerPool
from engine.algorithms.tensorflow.evolution_mutation import EvolutionWithMutationPlayerPool
from engine.games.draughts import BOARD_SIZE, LOGIC_INSTANCE
from engine.player import ParametrizedPlayer


class DraughtsCNNPlayer(ParametrizedPlayer):
    def __init__(self):
        super(DraughtsCNNPlayer, self).__init__()

        # fields are encoded as 4 boolean values: is_dark, is_me, is_enemy, is_king
        self.board_input = tf.placeholder(tf.float32, [None, BOARD_SIZE, BOARD_SIZE, 4])
        self.layers = [
            tf.layers.Conv2D(6, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(8, 3, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(10, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(10, 3, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(12, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(12, 3, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(12, 4, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.MaxPooling2D(2, 2),
            tf.layers.Dense(1)
        ]

        self.layers_out = self.board_input
        for layer in self.layers[:-1]:
            self.layers_out = layer(self.layers_out)

        estimated_and_reversed = self.layers[-1](tf.reshape(self.layers_out, [-1, int(12 * (BOARD_SIZE / 2) ** 2)]))
        out = tf.reduce_sum(tf.reshape(estimated_and_reversed, [-1, 2]), 1)

        self.output = out

    def _encode_view(self, view):
        base = [[[
            1. if view[(col, row)].is_dark else 0.,
            1. if view[(col, row)].player == self else 0.,
            1. if view[(col, row)].player not in (None, self) else 0.,
            1. if view[(col, row)].is_king else 0.,
        ] for row in range(BOARD_SIZE)] for col in range(BOARD_SIZE)]
        rotated = [[[
            1. if view[(col, row)].is_dark else 0.,
            1. if view[(col, row)].player not in (None, self) else 0.,
            1. if view[(col, row)].player == self else 0.,
            1. if view[(col, row)].is_king else 0.,
        ] for row in reversed(range(BOARD_SIZE))] for col in reversed(range(BOARD_SIZE))]
        return base, rotated

    def get_variable_list(self):
        variable_list = [variable for layer in self.layers for variable in layer.trainable_variables]
        return variable_list

    def get_next_move(self):
        moves = LOGIC_INSTANCE.list_moves(self.view)

        if len(moves) == 0:
            return None

        future_boards = [LOGIC_INSTANCE.apply_move(self.view, move) for move in moves]
        encoded = [enc for view in future_boards for enc in self._encode_view(view)]  # [enc, enc_rev, enc, enc_rev...]

        estimated = self.session.run(self.output, {self.board_input: encoded})

        return max(zip(moves, estimated), key=lambda move_est: move_est[1])[0]


class DraughtsEvolutionWithMutationPool(EvolutionWithMutationPlayerPool):
    def __init__(self, session,
                 stddev,
                 pool_size,
                 tournament_size):
        super(DraughtsEvolutionWithMutationPool, self).__init__(session,
                                                                DraughtsCNNPlayer,
                                                                stddev, pool_size, tournament_size,
                                                                True)


class DraughtsCNNOnePlusOnePool(OnePlusOnePlayerPool):
    def __init__(self, session,
                 sigma_proportion=1.2,
                 sigma_scaling_interval=10,
                 win_proportion=0.2):
        super(DraughtsCNNOnePlusOnePool, self).__init__(session, DraughtsCNNPlayer,
                                                        sigma_proportion, sigma_scaling_interval, win_proportion)
