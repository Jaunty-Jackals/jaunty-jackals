#!/usr/bin/env python3

"""
Curses output module
"""

import curses
import textwrap
import enum
from . import helpdocs

class _DrawCharacters:
    """
    Characters that are used for drawing the game
    """

    game_area_border_char = "="
    tile_border_char = "."
    tile_inner_char = " "
    piece_border_char = "x"
    piece_hl_char = "-"
    piece_vl_char = "|"
    piece_inner_char = " "

class _SubWindow:
    """
    Game sub-window

    This sub-window represents the base for the other, concrete
    sub-windows. It provides the base for drawing, and resizing the
    window.
    """

    _BORDER_WIDTH = 1

    def _update_draw_area_size_pos(self, new_width, new_height):
        self._draw_area_xy = (
                _SubWindow._BORDER_WIDTH,
                _SubWindow._BORDER_WIDTH)
        self._draw_area_wh = (
                new_width - 2 * _SubWindow._BORDER_WIDTH,
                new_height - 2 * _SubWindow._BORDER_WIDTH)

    def __init__(self, x, y, width, height):
        self._window = curses.newwin(height, width, y, x)
        self._update_draw_area_size_pos(width, height)

    def get_window_size(self):
        (win_height, win_width) = self._window.getmaxyx()
        return (win_width, win_height)

    def get_draw_area_size(self):
        return tuple(dim - 2 * _SubWindow._BORDER_WIDTH for
                dim in self.get_window_size())

    # needs to be separate method because it will be called from the
    # subclasses
    def _resize_window(self, new_width, new_height):
        self._window.resize(new_height, new_width)
        self._update_draw_area_size_pos(new_width, new_height)

    def resize_window(self, new_width, new_height):
        self._resize_window(new_width, new_height)

    def resize_draw_area(self, new_width, new_height):
        self._resize_window(
                new_width + 2 * _SubWindow._BORDER_WIDTH,
                new_height + 2 * _SubWindow._BORDER_WIDTH)

    def move_window(self, new_x, new_y):
        self._window.mvwin(new_y, new_x)

    def redraw(self):
        self._window.erase()
        self._window.border()
        self._actual_draw()
        self._window.refresh()

class _MessageWindow(_SubWindow):
    """
    Message window helper class

    This class represents the message window. Its position, and size are
    externaly specified. Its duties are to reflow, and repage the
    message text, so it can fit inside the window, and provide the
    drawing.
    """

    def __init__(self, title, message, x, y, width, height):
        super().__init__(x, y, width, height)

        self._title = title
        self._message = message

        self._reflow_message()

    def _reflow_message(self):
        self._message_lines = []

        for paragraph in self._message.splitlines():
            if paragraph != "":
                wrapped_paragraph = textwrap.wrap(
                        paragraph,
                        width = self._draw_area_wh[0])
                self._message_lines.extend(wrapped_paragraph)
            else:
                # [TODO] quick fix to avoid the skipping of newlines
                self._message_lines.append("")

        # sign change is done in order to get the ceiling while rounding
        # the real value
        self._num_pages = -(
                -len(self._message_lines) // self._draw_area_wh[1])

        self._page_index = 0

    def resize_window(self, new_width, new_height):
        super(_MessageWindow, self).resize_window(new_width, new_height)
        self._reflow_message()

    def _actual_draw(self):
        TITLE_INDENT = 2

        if self._num_pages > 1:
            # add the curr. page index in the title
            title_pages = self._title + " (page {} of {})".format(
                    self._page_index + 1, self._num_pages)
        else:
            title_pages = self._title

        prepared_title = textwrap.shorten(
                title_pages,
                width = self._draw_area_wh[0] - (TITLE_INDENT * 2),
                placeholder = "...")

        self._window.addstr(0, TITLE_INDENT, prepared_title)

        start_line = self._page_index * self._draw_area_wh[1]
        line_cnt = self._draw_area_wh[1]
        if start_line + line_cnt > len(self._message_lines):
            line_cnt = len(self._message_lines) - start_line

        for msg_line in range(0, line_cnt):
            self._window.addstr(
                    self._draw_area_xy[1] + msg_line,
                    self._draw_area_xy[0],
                    self._message_lines[start_line + msg_line])

    def get_num_pages(self):
        return self._num_pages

    def get_page_index(self):
        return self._page_index

    def set_page_index(self, index):
        self._page_index = index

class _BoardWindow(_SubWindow):
    """
    Board sub-window

    This window is used to represent the game board.
    """

    def __init__(self, x, y, width, height, board_wh_tiles, 
            free_tile_value):
        super().__init__(x, y, width, height)

        self._board_wh_tiles = board_wh_tiles
        self._free_tile_value = free_tile_value

        self._fit_window_to_board()

    def _calc_tile_board_size(self):
        """
        Calculate the size of tiles, and board, in characters
        """

        self._tile_wh = tuple(win_dim // cnt
                for (win_dim, cnt) in
                zip(self._draw_area_wh, self._board_wh_tiles))
        self._inside_tile_wh = tuple(
                tile_dim - 2 for tile_dim in self._tile_wh)
        return tuple(tile_dim * board_dim
                for (tile_dim, board_dim) in
                zip(self._tile_wh, self._board_wh_tiles))

    def _fit_window_to_board(self):
        (board_width, board_height) = self._calc_tile_board_size()
        super().resize_draw_area(board_width, board_height)

    def resize_window(self, new_width, new_height):
        super().resize_window(new_width, new_height)
        self._fit_window_to_board()

        return self.get_window_size()
    
    def change_board_dimensions(self, horizontal_tiles, vertical_tiles):
        self._board_wh_tiles = (horizontal_tiles, vertical_tiles)
        self._calc_tile_board_size()

    def set_board_pieces(self, pieces):
        self._pieces = pieces

    def _actual_draw(self):
        self._draw_tiles()
        self._draw_pieces()

    def _draw_tiles(self):
        dc = _DrawCharacters
        border_line = \
                dc.tile_border_char * self._draw_area_wh[0]
        inner_line_tile = "".join((
                dc.tile_border_char,
                dc.tile_inner_char * self._inside_tile_wh[0],
                dc.tile_border_char))
        inner_line = inner_line_tile * self._board_wh_tiles[0]

        draw_y = self._draw_area_xy[1]
    
        def draw_tile_line(line_text):
            nonlocal draw_y
            self._window.addstr(draw_y, self._draw_area_xy[0], 
                    line_text)
            draw_y += 1

        for tile_row in range(self._board_wh_tiles[1]):
            draw_tile_line(border_line)
            for inside_tile_row in range(self._inside_tile_wh[1]):
                draw_tile_line(inner_line)
            draw_tile_line(border_line)

    def _draw_pieces(self):
        for row in range(self._board_wh_tiles[1]):
            for col in range(self._board_wh_tiles[0]):
                piece_value = self._pieces[row][col]
                if piece_value != self._free_tile_value:
                    self._draw_piece(col, row, piece_value)

    def _draw_piece(self, tile_x, tile_y, value):
        dc = _DrawCharacters
        border_line = "".join((
                dc.piece_border_char,
                dc.piece_hl_char * self._inside_tile_wh[0],
                dc.piece_border_char))
        middle_empty_line = "".join((
                dc.piece_vl_char,
                dc.piece_inner_char * self._inside_tile_wh[0],
                dc.piece_vl_char))
        middle_value_line = "".join((
                dc.piece_vl_char,
                "{:{fill}^{width}d}".format(
                    value,
                    fill = dc.piece_inner_char,
                    width = self._inside_tile_wh[0]),
                dc.piece_vl_char))

        draw_x = tile_x * self._tile_wh[0] + self._draw_area_xy[0]
        draw_y = tile_y * self._tile_wh[1] + self._draw_area_xy[1]

        def draw_piece_line(line_text):
            nonlocal draw_y
            self._window.addstr(draw_y, draw_x, line_text)
            draw_y += 1

        draw_piece_line(border_line)

        for inner_row in range(self._inside_tile_wh[1]):
            if inner_row == self._inside_tile_wh[1] // 2:
                draw_piece_line(middle_value_line)
            else:
                draw_piece_line(middle_empty_line)

        draw_piece_line(border_line)

class CursesOutput:
    """
    Curses output class

    Encapsulate all the necessary data to provide the visual output of 
    the game to the specified curses window.
    """

    # number of lines used by the main window
    _MAIN_WINDOW_LINES = 3
    # number of message windows
    _MESSAGE_WINDOWS_CNT = 3

    class _MessageWindowIndices(enum.IntEnum):
        """
        Maps the indices in the window list to specific windows
        """

        mwi_intro = 0
        mwi_endgame = 1
        mwi_help = 2

    def __init__(self, window, game_ctrl):
        self._window = window
        self._message_windows = \
                [None] * CursesOutput._MESSAGE_WINDOWS_CNT

        self._game_ctrl = game_ctrl
        self._game_ctrl.attach_output(self)

        self._status_line_text = "Game status line"

        self._board = _BoardWindow(
                0, 2,
                2, 2, # filler values
                self._game_ctrl.get_board_dimensions(),
                self._game_ctrl.get_free_tile_value())
        self.update_size(False)
        self._create_message_window(
                CursesOutput._MessageWindowIndices.mwi_intro,
                "Hello, fellow user!",
                r"This is the realization of the 2048 game (http://gabrielecirulli.github.io/2048/) in Python. Press <ESC> to exit, '?' for help, any other key to continue.")
        self.update_game_state()

    def update_size(self, redraw = True):
        (win_height, win_width) = self._window.getmaxyx()
        (board_win_width, board_win_height) = (
                win_width,
                win_height - CursesOutput._MAIN_WINDOW_LINES)
        board_win_wh = self._board.resize_window(
                board_win_width, board_win_height)
        # because the board will fit to the size of the board, the main
        # window now needs to accomodate to it
        self._win_wh = (
                board_win_wh[0],
                board_win_wh[1] + CursesOutput._MAIN_WINDOW_LINES)

        self._update_message_window_sizes()

        if redraw:
            self.redraw()

    def redraw(self):
        self._window.erase()
        self._draw_outer_elements()
        self._window.refresh()

        self._board.redraw()

        for msg_window in self._message_windows:
            if msg_window != None:
                msg_window.redraw()

    def _draw_outer_elements(self):
        dc = _DrawCharacters

        draw_y = 0

        def draw_line(line_text):
            nonlocal draw_y
            # `insstr` needed because of the bottom line
            self._window.insstr(draw_y, 0, line_text)
            draw_y += 1

        # top info
        draw_line("2048 copy")
        draw_line("Score: {}".format(self._score))
        # status line
        draw_y = self._win_wh[1] - 1
        draw_line(self._status_line_text)

    def update_game_state(self):
        self._board.set_board_pieces(self._game_ctrl.get_board_state())
        self._score = self._game_ctrl.get_current_score()
        self.redraw()

    def _create_message_window(self, index, title, message):
        self._message_windows[index] = _MessageWindow(
                title, message,
                1, 1,
                self._win_wh[0] - 2, self._win_wh[1] - 2)

    def _remove_message_window(self, index):
        self._message_windows[index] = None

    def _update_message_window_sizes(self):
        for msg_win in self._message_windows:
            if msg_win != None:
                msg_win.resize_window(
                        self._win_wh[0] - 2,
                        self._win_wh[1] - 2)

    def open_help(self):
        self._create_message_window(
                CursesOutput._MessageWindowIndices.mwi_help,
                "2048 game help",
                helpdocs.get_help_text())
        self.redraw()

    def close_help(self):
        self._remove_message_window(
                CursesOutput._MessageWindowIndices.mwi_help)
        self.redraw()

    def open_endgame_message(self):
        endgame_message = "".join([
                "Sorry, no more moves available =(.",
                " Current score is {}.".format(self._score)])
        
        self._create_message_window(
                CursesOutput._MessageWindowIndices.mwi_endgame,
                "Game End",
                endgame_message)
        self.redraw()
    
    def close_endgame_message(self):
        self._remove_message_window(
                CursesOutput._MessageWindowIndices.mwi_endgame)
        self.redraw()

    def is_operational(self):
        """
        Get the operational state of the component

        Returns the information if this component is able to function
        properly.
        """

        no_msg_windows_opened = True

        for msg_win in self._message_windows:
            if msg_win != None:
                no_msg_windows_opened = False
                break

        return no_msg_windows_opened

    def close_intro_window(self):
        self._remove_message_window(
                CursesOutput._MessageWindowIndices.mwi_intro)
        self.redraw()

    def _get_top_window(self):
        top_win = None

        for msg_win in self._message_windows:
            if msg_win != None:
                top_win = msg_win

        return top_win

    def current_win_next_page(self):
        curr_win = self._get_top_window()

        if curr_win != None:
            current_page_index = curr_win.get_page_index()
            if current_page_index == curr_win.get_num_pages() - 1:
                curr_win.set_page_index(0)
            else:
                curr_win.set_page_index(current_page_index + 1)
            self.redraw()

    def current_win_previous_page(self):
        curr_win = self._get_top_window()

        if curr_win != None:
            current_page_index = curr_win.get_page_index()
            if current_page_index == 0:
                curr_win.set_page_index(curr_win.get_num_pages() - 1)
            else:
                curr_win.set_page_index(current_page_index - 1)
            self.redraw()
