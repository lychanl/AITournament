import random

import player


class MinMaxPlayer(player.Player):
    """ Class that implements MinMax algorithm
    basing on assumption that this player plays against other players
    where all other players pick worst possible moves for this one.
    """

    def __init__(self, game_logic, depth):
        """ Creates instance of player
        that makes moves according to the MinMax algorithm

        args:
            game_logic - an object that implements FiniteTurnGameLogic interface
            depth - integer > 0, depth of analysis - 1 means that only next move will be evaluated,
                    2 that also next player's move will be etc
        """
        super(MinMaxPlayer, self).__init__()

        self._game_logic = game_logic
        self.depth = depth

    def get_next_move(self):
        """ Returns next move based on MinMax algorithm.
        If multiple moves are equally good, returns
        """
        best_value = None
        best_moves = None

        for move in self._game_logic.list_moves(self.view):
            value = self._evaluate(move, self.view, 1)

            if best_value is None or best_value < value:
                best_value = value
                best_moves = [move]
            elif best_value == value:
                best_moves.append(move)

        random.choice(best_moves)

    def _evaluate(self, move, view, current_depth):
        new_view = self._game_logic.apply_move(view, move)

        if current_depth == self.depth or self._game_logic.is_view_terminal(new_view):
            return self._game_logic.evaluate_view(new_view)

        current_player = self._game_logic.get_current_player(new_view)

        best_value = None
        for move in self._game_logic.list_moves(new_view):
            value = self._evaluate(move, self.view, current_depth + 1)

            if best_value is None or \
                    current_player == self.id and value > best_value or \
                    current_player != self.id and value < best_value:
                best_value = value

        return best_value
