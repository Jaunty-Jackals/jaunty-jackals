#!/usr/bin/env python3

"""
Game controller module

Has `MovementDirections` enum, and the `GameController` class.
"""

import enum
import random

class MovementDirections(enum.Enum):
    """
    Piece movement directions

    Specifies possible directions when moving pieces.
    """

    up = 1
    down = 2
    left = 3
    right = 4

class _GameStates(enum.Enum):
    """
    Game controller states

    Lists all the states game controller can be in.
    """

    gs_active = 1
    gs_terminated = 2
    gs_endgame = 3
    gs_suspended = 4

class _Board:
    """
    Game board class

    Encapsulates the all manipulations with the game board.
    """

    def __init__(self, board_width, board_height, free_tile_value):
        """
        Creates an empty board with the given dimensions
        """

        self._board_width = board_width
        self._board_height = board_height
        self._free_tile_value = free_tile_value

        self.reset_board()

    def reset_board(self):
        """
        Resets board to the empty state
        """

        bwr = range(self._board_width)
        bhr = range(self._board_height)
        ftw = self._free_tile_value

        self._board = [[ftw for col in bwr] for row in bhr]

        self._free_tiles_cnt = \
                self._board_width * self._board_height

    def get_tile(self, row, col):
        """
        Returns the value of a tile on the given position
        """

        return self._board[row][col]

    def set_tile(self, row, col, value):
        """
        Sets the value of a tile on the given position
        """

        new_tile_empty = value == self._free_tile_value
        old_tile_empty = \
                self._board[row][col] == self._free_tile_value

        if new_tile_empty and not old_tile_empty:
            self._free_tiles_cnt += 1
        elif not new_tile_empty and old_tile_empty:
            self._free_tiles_cnt -= 1

        self._board[row][col] = value

    def get_board_dimensions(self):
        """
        Returns the board width, and height, in tiles
        """

        return (self._board_width, self._board_height)

    def get_free_tile_value(self):
        """
        Returns the value used to indicate a free tile
        """

        return self._free_tile_value

    def get_free_tiles_cnt(self):
        """
        Returns the number of free tiles on the board
        """

        return self._free_tiles_cnt

    def generate_piece(self):
        """
        Generate new piece on the randomly selected free tile
        """

        new_free_tile_index = random.randint(
                0, self._free_tiles_cnt - 1)
        new_piece_value = 2 ** random.randint(1, 2)
        #new_piece_value = 2 ** random.randint(1, 12)

        new_piece_inserted = False
        current_free_tile_index = 0

        for row in range(0, self._board_width):
            for col in range(0, self._board_height):
                if self._board[row][col] == self._free_tile_value:
                    if current_free_tile_index == new_free_tile_index:
                        self._board[row][col] = new_piece_value
                        self._free_tiles_cnt -= 1
                        return
                    else:
                        current_free_tile_index += 1

    def get_whole_board(self):
        """
        Returns the whole board
        """

        return self._board

class GameController:
    """
    Game controller class

    Contains everything needed to represent, and control one instance of 
    the game.
    """

    def __init__(self,
            board_width = 4, board_height = 4,
            free_tile_value = 0):
        """
        Create the board in the initial state, ready to play
        """

        self._board = _Board(board_width, board_height, free_tile_value)
        self._state = _GameStates.gs_suspended

        self._output_ctrl = None
        self._input_ctrl = None

        self._reset_game_state()

    # controller info
    #

    def is_active(self):
        """
        Returns true value if the game is running
        """

        return self._state != _GameStates.gs_terminated

    def get_board_dimensions(self):
        """
        Return the board width, and height, in tiles
        """

        return self._board.get_board_dimensions()

    def get_board_state(self):
        """
        Returns the board state, that is, the board with pieces
        """

        return self._board.get_whole_board()

    def get_free_tile_value(self):
        return self._board.get_free_tile_value()

    def get_current_score(self):
        """
        Returns the current score
        """

        return self._current_score

    # controller actions
    #

    def attach_output(self, output_ctrl):
        """
        Attach the output controller
        """

        self._output_ctrl = output_ctrl

    def attach_input(self, input_ctrl):
        """
        Attach the input controller
        """

        self._input_ctrl = input_ctrl

    def reset_game(self):
        """
        Resets the game

        This method performs the full reset. The whole game controller 
        will be put in the initial state, as it was when the game was 
        first run.
        """

        # method state-dependent operation:
        #
        # state         operation
        # ------------- ------------------------------------------------
        # gs_active     resets the game
        # gs_terminated does nothing
        # gs_endgame    resets the game
        # gs_suspended  does nothing

        perform_reset = \
                self._state == _GameStates.gs_active or \
                self._state == _GameStates.gs_endgame

        if perform_reset:
            self._reset_game_state()
            self._output_ctrl.update_game_state()
            self._output_ctrl.close_endgame_message()

        # method state-changing operation:
        #
        # from state    to state        condition
        # ------------- --------------- --------------------------------
        # gs_endgame    gs_active       unconditionally

        if self._state == _GameStates.gs_endgame:
            self._state = _GameStates.gs_active

    def close_game(self):
        """
        Terminate the execution of the game
        """
        # method state-changing operation:
        #
        # from state    to state        condition
        # ------------- --------------- --------------------------------
        # any           gs_terminated   uncond.

        self._state = _GameStates.gs_terminated

    def move_pieces(self, movement_direction):
        """
        Piece movement, and merge, for the whole board

        Performs the piece movement, and merging, in the given direction 
        for the whole board. After that, checks if there are available
        moves.
        """

        # method state-dependent operation:
        #
        # state         operation
        # ------------- ------------------------------------------------
        # gs_active     move, and merge pieces
        # gs_terminated does nothing
        # gs_endgame    does nothing
        # gs_suspended  does nothing

        if self._state == _GameStates.gs_active:
            md = movement_direction
            mds = MovementDirections
            (bw, bh) = self._board.get_board_dimensions()

            movement_done = False

            transl_map = {
                    mds.up:     lambda pr_ind, sc_ind: \
                            (pr_ind, sc_ind),
                    mds.down:   lambda pr_ind, sc_ind: \
                            (bh - pr_ind - 1, sc_ind),
                    mds.left:   lambda pr_ind, sc_ind: \
                            (sc_ind, pr_ind),
                    mds.right:  lambda pr_ind, sc_ind: \
                            (sc_ind, bw - pr_ind - 1)}

            iter_limit_map = {
                    mds.up:     (bw, bh),
                    mds.down:   (bw, bh),
                    mds.left:   (bh, bw),
                    mds.right:  (bh, bw)}

            (outer_iter_limit, dir_line_length) = iter_limit_map[md]
            coord_transl_f = transl_map[md]

            for sc_ind in range(outer_iter_limit):
                def getter(index):
                    return self._board.get_tile(
                            *coord_transl_f(index, sc_ind))
                def setter(index, value):
                    (row, col) = coord_transl_f(index, sc_ind)
                    self._board.set_tile(row, col, value)

                (ret_score, ret_movement_done) = \
                        self._move_merge_pieces_dl(
                        dir_line_length, getter, setter)

                self._current_score += ret_score
                movement_done = movement_done or ret_movement_done

            if (movement_done):
                self._board.generate_piece()
                self._output_ctrl.update_game_state()

        # method state-changing operation:
        #
        # from state    to state        condition
        # ------------- --------------- --------------------------------
        # gs_active     gs_endgame      no moves available

        go_to_endgame = \
                self._state == _GameStates.gs_active and \
                not self._moves_available()
        
        if go_to_endgame:
            self._state = _GameStates.gs_endgame
            self._output_ctrl.open_endgame_message()

    def suspend_game(self):
        """
        Suspend the game
        """

        # method state-changing operation:
        #
        # from state    to state        condition
        # ------------- --------------- --------------------------------
        # gs_active     gs_suspended    unconditionally

        if self._state == _GameStates.gs_active:
            self._state = _GameStates.gs_suspended

    def resume_game(self):
        """
        Resume the game
        """

        # method state-changing operation:
        #
        # from state    to state        condition
        # ------------- --------------- --------------------------------
        # gs_suspended  gs_active       other controllers are oper.

        resume_cond = \
                self._state == _GameStates.gs_suspended and \
                self._output_ctrl.is_operational() and \
                self._input_ctrl.is_operational()

        if resume_cond:
            self._state = _GameStates.gs_active

    # auxiliary operations
    #

    def _move_merge_pieces_dl(self, dl_length, get_piece, set_piece):
        """
        Move and merge the pieces on the direction line

        Helper function for moving, and merging the pieces on the given
        direction line, as specified by the required game logic.

        Manipulation with the direction line is performed through the 
        getter, and setter functions provided as the funcion parameters.

        Function returns the cumulative score of the mergings, as well 
        as the information if any piece was moved.
        """

        cursor_index = 0
        free_tile_index = -1
        merging_piece_index = -1

        merging_score = 0
        movement_done = False

        ftw = self._board.get_free_tile_value()

        while cursor_index < dl_length:
            piece_val = get_piece(cursor_index)

            if piece_val == ftw:
                # the tile is free

                if free_tile_index == -1:
                    # free tile cursor is unset

                    free_tile_index = cursor_index

                cursor_index += 1
            else:
                # piece is found

                if merging_piece_index != -1:
                    # merging available

                    if get_piece(merging_piece_index) == piece_val:
                        # the pieces are the same

                        # merge pieces
                        set_piece(cursor_index, ftw)
                        set_piece(merging_piece_index, piece_val * 2)

                        merging_score += piece_val
                        movement_done = True

                        merging_piece_index = -1
                    elif free_tile_index != -1:
                        # no merging, but there is a free tile

                        # move the piece to the free tile
                        set_piece(free_tile_index, piece_val)
                        set_piece(cursor_index, ftw)

                        merging_piece_index = free_tile_index

                        movement_done = True

                        free_tile_index += 1
                        cursor_index += 1
                    else:
                        # no merging, and no free tiles

                        merging_piece_index = cursor_index
                        cursor_index += 1
                else:
                    # merging unavailable

                    if free_tile_index != -1:
                        # there is a free tile

                        # move the piece to the free tile
                        set_piece(free_tile_index, piece_val)
                        set_piece(cursor_index, ftw)

                        merging_piece_index = free_tile_index

                        movement_done = True

                        free_tile_index += 1
                        cursor_index += 1
                    else:
                        # no free tiles

                        merging_piece_index = cursor_index
                        cursor_index += 1

        return (merging_score, movement_done)

    def _moves_available(self):
        """
        Check if there are any valid moves available
        """

        # first check - are there free tiles?
        #

        if self._board.get_free_tiles_cnt() > 0:
            return True

        # second check - are there mergings available?
        #

        (bw, bh) = self._board.get_board_dimensions()

        # first pass - check by rows
        for row in range(bh):
            for col in range(bw - 1):
                curr_piece_val = self._board.get_tile(row, col)
                next_piece_val = self._board.get_tile(row, col + 1)

                if curr_piece_val == next_piece_val:
                    return True

        # second pass - check by columns
        for col in range(bw):
            for row in range(bh - 1):
                curr_piece_val = self._board.get_tile(row, col)
                next_piece_val = self._board.get_tile(row + 1, col)

                if curr_piece_val == next_piece_val:
                    return True

        return False

    def _reset_game_state(self):
        """
        Resets the game state
        """

        self._board.reset_board()

        for i in range(2):
        #for i in range(15):
            self._board.generate_piece()

        self._current_score = 0
