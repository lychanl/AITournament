import tensorflow as tf

from engine.algorithms.tensorflow.one_plus_one_pool import OnePlusOnePlayer, OnePlusOnePlayerPool
from engine.games.draughts import BOARD_SIZE, LOGIC_INSTANCE


class DraughtsCNNPlayer(OnePlusOnePlayer):
    def __init__(self):
        super(DraughtsCNNPlayer, self).__init__()

        # fields are encoded as 4 boolean values: is_dark, is_me, is_enemy, is_king
        self.board_input = tf.placeholder(tf.float32, [None, BOARD_SIZE, BOARD_SIZE, 4])
        self.layers = [
            tf.layers.Conv2D(8, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(16, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(20, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(24, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.Conv2D(24, 2, padding="same", activation=tf.nn.leaky_relu),
            tf.layers.MaxPooling2D(2, 2),
            tf.layers.Dense(1)
        ]

        out = self.board_input
        for layer in self.layers[:-1]:
            out = layer(out)

        out = self.layers[-1](tf.reshape(out, [-1, int(24 * (BOARD_SIZE / 2) ** 2)]))

        self.output = out

    def _encode_view(self, view):
        return [[[
            1. if view[(col, row)].is_dark else 0.,
            1. if view[(col, row)].player == self.id else 0.,
            1. if view[(col, row)].player not in (None, self.id) else 0.,
            1. if view[(col, row)].is_king else 0.,
        ] for row in range(BOARD_SIZE)] for col in range(BOARD_SIZE)]

    def get_variable_list(self):
        variable_list = [variable for layer in self.layers for variable in layer.trainable_variables]
        return variable_list

    def get_next_move(self):
        moves = LOGIC_INSTANCE.list_moves(self.view)

        if len(moves) == 0:
            return None

        future_boards = [LOGIC_INSTANCE.apply_move(self.view, move) for move in moves]
        encoded = [self._encode_view(view) for view in future_boards]

        estimated = self.session.run(self.output, {self.board_input: encoded})

        return max(zip(moves, estimated), key=lambda move_est: move_est[1])[0]


class DraughtsCNNOnePlusOnePool(OnePlusOnePlayerPool):
    def __init__(self, session):
        super(DraughtsCNNOnePlusOnePool, self).__init__(session, DraughtsCNNPlayer)
