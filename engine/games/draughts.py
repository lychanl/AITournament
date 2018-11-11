import os

from engine.game import FiniteTurnGameLogic
from engine.algorithms.minmax_player import MinMaxPlayer

BOARD_SIZE = 10
PLAYER_EMPTY_MOVES = 15
SINGLE_PLAYER_3_1_EMPTY_MOVES = 15


class Field:
    def __init__(self, is_dark, player=None, is_king=False):
        self.is_dark = is_dark
        self.player = player
        self.is_king = is_king


class DraughtsView:
    def __init__(self, base_view=None, changes=None, change_pov=False, next_move=False):
        if base_view is None:
            self.fields = [
                [Field(is_dark=(i + j) % 2 == 0) for j in range(BOARD_SIZE)]
                for i in range(BOARD_SIZE)]

            self.pov = None
            self.other = None
            self.previous_states = {}
            self.is_terminal = False
            self.winner = None
            self.black = None
            self.white = None

        else:
            self.fields = [
                [Field(field.is_dark, field.player, field.is_king) for field in column]
                for column in base_view.fields]
            self.is_terminal = base_view.is_terminal
            self.winner = base_view.winner
            self.previous_states = dict(base_view.previous_states)
            self.black = base_view.black
            self.white = base_view.white

            if changes is not None:
                for (col, row), field in changes:
                    self.fields[col][row] = field

            if change_pov:
                self.pov = base_view.other
                self.other = base_view.pov
                if self.winner == self.pov:
                    self.winner = self.other
                if self.winner == self.other:
                    self.winner = self.pov

                self.fields.reverse()
                for col in self.fields:
                    col.reverse()
            else:
                self.pov = base_view.pov
                self.other = base_view.other

            if next_move:
                pov_has_moves = False
                other_has_moves = False
                pov_single_king_checker = 0
                other_single_king_checker = 0

                for col in range(BOARD_SIZE):
                    for row in range(BOARD_SIZE):
                        field = self.fields[col][row]
                        if field.player == self.pov:
                            if field.is_king:
                                pov_single_king_checker += 1
                            else:
                                pov_single_king_checker += 2
                            if not pov_has_moves:
                                pov_has_moves = self._can_piece_move(col, row)

                        elif not other_has_moves and field.player == self.other:
                            if field.is_king:
                                other_single_king_checker += 1
                            else:
                                other_single_king_checker += 2
                            if not other_has_moves:
                                other_has_moves = self._can_piece_move(col, row)

                if not pov_has_moves:
                    self.is_terminal = True
                    self.winner = self.other
                elif not other_has_moves:
                    self.is_terminal = True
                    self.winner = self.pov
                elif pov_single_king_checker == 1 and other_single_king_checker == 1:
                    self.is_terminal = True
                    self.winner = None
                else:
                    state = self._encode_state()
                    if state in self.previous_states:
                        self.previous_states[state] += 1
                    else:
                        self.previous_states[state] = 1
                    if self.previous_states[state] >= 3:
                        self.is_terminal = True
                        self.winner = None

    def _encode_state(self):
        state = []
        for col in range(BOARD_SIZE):
            offset = 0 if self.fields[col][0].is_dark else 1
            for in_row in range(BOARD_SIZE // 2):
                field = self.fields[col][offset + in_row]
                if field.player is not None:
                    state.append((1 if field.is_king else 2) + (0 if field.player == self.pov else 2))
                else:
                    state.append(0)
        return self.pov, bytes(state)

    def _can_piece_move(self, col, row):
        field = self.fields[col][row]
        for dir_col in -1, 1:
            for dir_row in -1, 1:
                c = col + dir_col
                r = row + dir_row
                if 0 <= c < BOARD_SIZE and 0 <= r < BOARD_SIZE:
                    if self.fields[c][r].player is None and (dir_col > 0 or field.is_king):
                        return True
                    if self.fields[c][r].player != field.player:
                        c += dir_col
                        r += dir_row
                        if 0 <= c < BOARD_SIZE and 0 <= r < BOARD_SIZE:
                            if self.fields[c][r].player is None:
                                return True

        return False

    def begin(self, white_player, black_player):
        for col in self.fields:
            for field_id in range(BOARD_SIZE):
                field = col[field_id]
                if field.is_dark:
                    if field_id < BOARD_SIZE // 2 - 1:
                        field.player = white_player
                    elif field_id > BOARD_SIZE // 2:
                        field.player = black_player
        self.pov = self.white = white_player
        self.other = self.black = black_player

    def __getitem__(self, key):
        return self.fields[key[0]][key[1]]

    def __str__(self):
        ret = "===========" + os.linesep
        ret += "White: " + str(self.white) + os.linesep
        ret += "Black: " + str(self.black) + os.linesep

        if self.pov == self.white:
            ret += "===BLACK===" + os.linesep
        else:
            ret += "===WHITE===" + os.linesep

        to_print = ["" for _ in range(BOARD_SIZE)]

        for col in reversed(self.fields):
            for field_id in reversed(range(BOARD_SIZE)):
                field = col[field_id]
                if not field.is_dark:
                    to_print[field_id] += " "
                elif field.player == self.white and self.white is not None:
                    to_print[field_id] += "W" if field.is_king else "w"
                elif field.player == self.black and self.black is not None:
                    to_print[field_id] += "B" if field.is_king else "b"
                else:
                    to_print[field_id] += "."

        for row in reversed(to_print):
            ret += row + os.linesep

        if self.pov == self.white:
            ret += "===WHITE==="
        else:
            ret += "===BLACK==="
        if self.is_terminal:
            if self.winner is not None:
                ret += "GAME OVER! Winner: " + str(self.winner)
            else:
                ret += "GAME OVER! DRAW!"

        return ret


class DraughtsMove:
    def __init__(self, from_):
        self.from_ = from_
        self.list = list()

    def add_move(self, to):
        self.list.append(to)

    def __len__(self):
        return len(self.list)


class DraughtsLogic(FiniteTurnGameLogic):
    def get_current_player(self, game_view):
        return game_view.pov

    def list_moves(self, game_view):
        moves = []
        moves_captures = 0

        for col in range(BOARD_SIZE):
            for row in range(BOARD_SIZE):
                if game_view[(col, row)].player == game_view.pov:
                    piece_moves, captures = self._list_moves(game_view, col, row, col, row)

                    piece_moves = [[(col, row)] + move for move in piece_moves]
                    if captures == moves_captures:
                        moves.extend(piece_moves)
                    elif captures > moves_captures:
                        moves = piece_moves
                        moves_captures = captures

        return moves

    def _list_moves(self, view, col, row, cur_col, cur_row, captures=list()):
        field = view.fields[col][row]
        moves = []
        longest = 0
        for dir_col in -1, 1:
            to_board_end_x = cur_col + 1 if dir_col < 0 else BOARD_SIZE - cur_col
            for dir_row in -1, 1:
                to_board_end_y = cur_row + 1 if dir_row < 0 else BOARD_SIZE - cur_row
                dir_moves = []
                dir_moves_have_captures = False

                capture = None
                for dist in range(1, min(to_board_end_x, to_board_end_y)):
                    if not field.is_king and (dist > 2 or dist == 2 and capture is None):
                        break
                    c = dir_col * dist + cur_col
                    r = dir_row * dist + cur_row
                    cur_field = view.fields[c][r]

                    if cur_field.player == view.pov and (c, r) != (col, row):  # stepped on own piece
                        break

                    if cur_field.player == view.other:
                        if (c, r) in captures:  # move over captured piece
                            break
                        elif capture is None:
                            capture = (c, r)
                            continue
                        else:
                            break

                    # cur_field.player is None
                    if len(captures) == 0 and capture is None and (field.is_king or dir_row > 0):
                        dir_moves.append([(c, r)])
                        if not field.is_king:
                            break
                    elif capture is not None:
                        if not dir_moves_have_captures:
                            dir_moves_have_captures = True
                            dir_moves = []
                        further_captures, _ = self._list_moves(view, col, row, c, r, captures + [capture])
                        if len(further_captures) == 0:
                            dir_moves.append([(c, r)])
                        else:
                            dir_moves.extend([[(c, r)] + f for f in further_captures])

                if len(dir_moves) > 0:
                    m_length = len(max(dir_moves, key=len)) if dir_moves_have_captures else 0
                    if m_length > 1:
                        dir_moves = [move for move in dir_moves if len(move) == m_length]

                    if m_length > longest:
                        moves = dir_moves
                        longest = m_length
                    elif m_length == longest:
                        moves += dir_moves

        return moves, longest

    def is_view_terminal(self, game_view):
        return game_view.is_terminal

    def apply_move(self, game_view, move):  # without validating length
        assert game_view[move[0]].player == game_view.pov

        is_king = game_view[move[0]].is_king
        coord = move[0]
        removed_pieces_coord = []

        for move_part in move[1:]:
            col_diff = move_part[0] - coord[0]
            row_diff = move_part[1] - coord[1]

            assert abs(col_diff) == abs(row_diff) and col_diff != 0
            assert game_view[move_part].player is None or move_part == coord

            if not is_king:
                if row_diff <= 0:
                    assert row_diff == -2
                else:
                    assert row_diff <= 2

                if abs(row_diff) == 2:
                    skipped = (coord[0] + col_diff // 2, coord[1] + row_diff // 2)
                    assert game_view[skipped].player == game_view.other
                    assert skipped not in removed_pieces_coord
                    removed_pieces_coord.append(skipped)
                else:
                    assert len(move) == 2

            else:
                col_step = col_diff // abs(col_diff)
                row_step = row_diff // abs(row_diff)
                was_enemy_piece = False

                for steps in range(1, abs(col_diff)):
                    skipped = (col_step * steps, row_step * steps)
                    if game_view[skipped].player == game_view.other:
                        assert skipped not in removed_pieces_coord
                        assert not was_enemy_piece
                        removed_pieces_coord.append(skipped)

                        was_enemy_piece = True

                if not was_enemy_piece:
                    assert len(move) == 2
            coord = move_part

        if coord[1] == BOARD_SIZE - 1:
            # promotion
            is_king = True

        changes = [
            (move[0], Field(True)),
        ]

        for removed in removed_pieces_coord:
            changes.append((removed, Field(True)))

        changes.append((coord, Field(True, game_view.pov, is_king)))

        return DraughtsView(game_view, changes, True, True)

    def evaluate_view(self, view, viewpoint_player):
        points_current = 0
        points_other = 0
        for col in view.fields:
            for field in col:
                if field.player == viewpoint_player:
                    points_current += 3.5 if field.is_king else 1
                elif field.player is not None:
                    points_other += 3.5 if field.is_king else 1

        if view.winner is None:
            return points_current - points_other
        elif view.winner == viewpoint_player:
            return points_current + 1000
        else:
            return -(points_other + 1000)


LOGIC_INSTANCE = DraughtsLogic()


class MinMaxDraughtsPlayer(MinMaxPlayer):
    def __init__(self, depth):
        super(MinMaxDraughtsPlayer, self).__init__(LOGIC_INSTANCE, depth)
