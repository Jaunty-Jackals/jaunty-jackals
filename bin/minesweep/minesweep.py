import curses
import random
from collections import namedtuple
from enum import Enum
from math import sqrt
from platform import system
from typing import Any, Generator, Union

from minesweep_utils import Rect, draw_rect, minmax, open_menu
from play_sounds import play_file as playsound
from play_sounds import play_while_running

path = "bin/utils/sound/sfx_minesweeper_"
sfx_nav_path = path + "nav.wav"
sfx_space_path = path + "space.wav"
sfx_enter_path = path + "flag.wav"
sfx_death_path = path + "death.wav"
sfx_bgm_path = path + "bgm.wav"
sfx_ingame_path = path + "ingame.wav"


class Flags(Enum):
    """Enum to define all possible state related flags"""

    INITIAL = 0
    MARKED = 1
    REVEALED = 2


class Table:
    """Table class to have rows * cols as a list"""

    def __init__(self, cols: int, rows: int, default: int = 0):
        if (cols <= 0) or (rows <= 0):
            raise ValueError("Invalid rows/cols provided for table")
        self.table = [default for c in range(cols * rows)]
        self.num_cols = cols
        self.num_rows = rows

    def size(self) -> int:
        """Returns total size of table"""
        return self.num_cols * self.num_rows

    def __getitem__(self, key: tuple) -> Union[list, int]:
        try:
            x, y = key
            if x >= self.num_cols or y >= self.num_rows:
                raise IndexError("list index out of range")
            return self.table[self.subscript_to_linear(x, y)]
        except TypeError:
            return self.table[key]

    def __setitem__(self, key: tuple, value: int):
        try:
            x, y = key
            if x >= self.num_cols or y >= self.num_rows:
                raise IndexError("list index out of range")
            self.table[self.subscript_to_linear(x, y)] = value
        except TypeError:
            self.table[key] = value

    def neighbours(self, x: int, y: int) -> None:
        """Yields all current neighbours of cell"""
        for c in range(max(x - 1, 0), min(x + 2, self.num_cols)):
            for r in range(max(y - 1, 0), min(y + 2, self.num_rows)):
                if c != x or r != y:
                    yield c, r

    def linear_to_subscript(self, index: int) -> tuple:
        """Convert string to tuple"""
        return index % self.num_cols, index // self.num_cols

    def subscript_to_linear(self, col: int, row: int) -> int:
        """Convert tuple back to string"""
        return col + row * self.num_cols

    def count(self, value: int) -> int:
        """Returns number of values in the table"""
        return self.table.count(value)

    def row(self, r: int) -> list:
        """Returns particular row from the table"""
        start = self.subscript_to_linear(0, r)
        return self.table[start : start + self.num_cols]

    def __iter__(self):
        for y in range(self.num_rows):
            for x in range(self.num_cols):
                yield self[x, y]


class MineSweeper:
    """Main minesweeper class to define the minesweeper game"""

    def __init__(self, mines: Table, flags: Table = None):
        """Default init function"""
        if flags is None:
            flags = Table(mines.num_cols, mines.num_rows, Flags.INITIAL)
        if mines.size() != flags.size():
            raise ValueError(
                "Fields cannot have different sizes ({0} != {1})".format(
                    mines.size(), flags.size()
                )
            )
        self.mines = mines
        self.flags = flags
        self.hints = Table(mines.num_cols, mines.num_rows, 0)

        for i, _ in enumerate(self.hints):
            self.hints[i] = self.hint(*self.hints.linear_to_subscript(i))

    def rows(self) -> int:
        """Returns num of rows in game"""
        return self.mines.num_rows

    def columns(self) -> int:
        """Returns num of columns in game"""
        return self.mines.num_cols

    def hint(self, x: int, y: int) -> int:
        """Returns number of mines around current cell"""
        if self.mines[x, y]:
            return -1
        else:
            h = 0
            for a, b in self.mines.neighbours(x, y):
                if self.mines[a, b]:
                    h += 1
            return h

    def is_solved(self) -> bool:
        """Function to check if it's solved"""
        for mine, flag in zip(self.mines, self.flags):
            if mine and flag != Flags.MARKED:
                return False
        return True

    def is_lost(self) -> bool:
        """Function to check if outcome is lost"""
        for mine, flag in zip(self.mines, self.flags):
            if mine and flag == Flags.REVEALED:
                return True
        return False

    def auto_mark(self) -> None:
        """Marks cell for flag/mine"""
        for mine, flag in zip(self.mines, self.flags):
            if not mine and flag != Flags.REVEALED:
                return False

        for i, mine in enumerate(self.mines):
            if mine:
                self.flags[i] = Flags.MARKED
            else:
                self.flags[i] = Flags.REVEALED

    def reveal_all(self) -> None:
        """Function to reveal the final board"""
        for i, flag in enumerate(self.flags):
            if flag != Flags.MARKED:
                self.flags[i] = Flags.REVEALED

    def reveal(self, x: int, y: int, reveal_known: bool = True) -> bool:
        """Function to reveal individual box"""
        if self.flags[x, y] == Flags.MARKED:
            self.flags[x, y] = Flags.INITIAL
        elif self.flags[x, y] == Flags.REVEALED:
            if self.hints[x, y] <= 0 or not reveal_known:
                return True
            neighbours = list(self.mines.neighbours(x, y))
            neighbour_mines = [
                (nx, ny) for nx, ny in neighbours if self.flags[nx, ny] == Flags.MARKED
            ]
            if len(neighbour_mines) == self.hints[x, y]:
                for nx, ny in neighbours:
                    if (nx, ny) not in neighbour_mines:
                        self.reveal(nx, ny, reveal_known=False)
        else:
            self.flags[x, y] = Flags.REVEALED
            if self.mines[x, y]:
                return False
            else:
                if self.hint(x, y) == 0:
                    for nx, ny in self.mines.neighbours(x, y):
                        if self.flags[nx, ny] == Flags.INITIAL:
                            self.reveal(nx, ny, reveal_known=False)
                self.auto_mark()
        return True

    def toggle_mark(self, x: int, y: int) -> None:
        """Toggle state of non-mine cells"""
        if self.flags[x, y] == Flags.INITIAL:
            self.flags[x, y] = Flags.MARKED
        elif self.flags[x, y] == Flags.MARKED:
            self.flags[x, y] = Flags.INITIAL
        self.auto_mark()

    @classmethod
    def create_random(cls, cols: int, rows: int, num_mines: int):
        """Creates random minesweeper for start"""
        mines = Table(cols, rows, False)
        flags = Table(cols, rows, Flags.INITIAL)

        fields = [(c, r) for c in range(cols) for r in range(rows)]
        for x, y in random.sample(fields, num_mines):
            mines[x, y] = True
        return MineSweeper(mines, flags)


def start_new_game(curse_context: Any) -> None:
    """Menu to start a new game"""
    with play_while_running(sfx_bgm_path, block=True):
        boxes = int(
            open_menu(
                curse_context, items=("100", "400", "625"), header="Number of Boxes"
            )
        )
        mine_percents = [0.1, 0.2, 0.4, 0.6]
        mines = [str(int(boxes * mp)) for mp in mine_percents]
        sel_mines = int(
            float(
                open_menu(curse_context, items=tuple(mines), header="Number of Mines")
            )
        )

        final_cols = int(minmax(sqrt(boxes), 0, curses.COLS - 3))
        final_rows = int(minmax(sqrt(boxes), 0, curses.LINES - 5))

    with play_while_running(sfx_ingame_path, block=True):
        start_game(curse_context, final_cols, final_rows, sel_mines)


def cursor_to_index(cursor_pos: Any, game_rect: Rect) -> Any:
    """Returns window position to table index"""
    return (cursor_pos.x - game_rect.x) // 2, cursor_pos.y - game_rect.y


def get_header(curse_context: Any, game: Any) -> Rect:
    """Returns the header for the game"""
    if game.is_solved():
        text = "Congratulations, You Won!"
    elif game.is_lost():
        text = "You Lost!"
    else:
        remaining = game.mines.count(True) - game.flags.count(Flags.MARKED)
        text = "Remaining Mines: {0}".format(remaining)
    curse_context.addstr(0, 0, text, curses.A_REVERSE)
    return Rect(0, 0, curses.COLS - 1, 1)


def get_footer(curse_context: Any, game: Any) -> Rect:
    """Returns the footer for the game"""
    if game.is_lost() or game.is_solved():
        controls = [("Press any key to continue", "")]
    else:
        controls = [
            ("Navigate:", "\u2190 \u2192 \u2191 \u2193"),
            ("Reveal:", "Space \u2423"),
            ("Toggle Mark:", "Enter \u23CE"),
            ("Menu:", "Escape Esc"),
        ]
    offset = 0
    for name, control in controls:
        curse_context.addstr(curses.LINES - 1, offset, name, curses.A_REVERSE)
        offset += len(name)
        curse_context.addstr(curses.LINES - 1, offset, " " + control + " ")
        offset += len(control) + 2
    return Rect(0, curses.LINES - 1, curses.COLS - 1, 1)


def get_game(curse_context: Any, game: Any, game_rect: Rect) -> Rect:
    """Returns main body of the game"""
    rect = Rect(game_rect.x, game_rect.y, game.columns() * 2 + 1, game.rows() + 2)
    rect = draw_rect(curse_context, rect)

    for i, (mine, flag, hint) in enumerate(zip(game.mines, game.flags, game.hints)):
        x, y = game.mines.linear_to_subscript(i)
        x = x * 2 + rect.x
        y = y + rect.y

        # OS-specific mine and flag text
        sym_initial = "\u25A0"
        sym_marked = "\u26F3"
        sym_mine = "\u26ED"

        if system().upper() in ("WINDOWS", "DARWIN"):
            sym_initial = "?"
            sym_marked = "M"
            sym_mine = "*"

        if flag == Flags.INITIAL:
            curse_context.addstr(y, x, sym_initial)
        elif flag == Flags.MARKED:
            curse_context.addstr(y, x, sym_marked, curses.color_pair(9))
        else:
            if mine:
                curse_context.addstr(y, x, sym_mine, curses.color_pair(8))
            else:
                if hint == 0:
                    curse_context.addstr(y, x, " ")
                elif hint == 1:
                    curse_context.addstr(y, x, str(hint), curses.color_pair(1))
                elif hint == 2:
                    curse_context.addstr(y, x, str(hint), curses.color_pair(2))
                elif hint == 3:
                    curse_context.addstr(y, x, str(hint), curses.color_pair(3))
                elif hint == 4:
                    curse_context.addstr(y, x, str(hint), curses.color_pair(4))
                else:
                    curse_context.addstr(y, x, str(hint), curses.color_pair(4))
    return rect


def draw_all(curse_context: Any, game: Any) -> Any:
    """Draws the main game"""
    game_head = get_header(curse_context, game)
    game_foot = get_footer(curse_context, game)
    game_body = Rect(
        0,
        game_head.height,
        curses.COLS - 1,
        curses.LINES - 1 - game_head.height - game_foot.height,
    )
    full_game = get_game(curse_context, game, game_body)
    return full_game


def start_game(curse_context: Any, cols: int, rows: int, mines: int) -> None:
    """Main loop to create and start the game"""
    game = MineSweeper.create_random(cols, rows, mines)

    Point = namedtuple("Point", ["x", "y"])
    cursor_pos = Point(0, 0)

    while True:
        curse_context.clear()
        game_rect = draw_all(curse_context, game)

        cursor_pos = Point(
            minmax(cursor_pos.x, game_rect.x, game_rect.x + game_rect.width - 1),
            minmax(cursor_pos.y, game_rect.y, game_rect.y + game_rect.height - 1),
        )
        curse_context.move(cursor_pos.y, cursor_pos.x)
        curse_context.refresh()

        input_ch = curse_context.getch()
        if input_ch == curses.KEY_LEFT:
            playsound(sfx_nav_path, block=False)
            cursor_pos = Point(cursor_pos.x - 2, cursor_pos.y)
        if input_ch == curses.KEY_RIGHT:
            playsound(sfx_nav_path, block=False)
            cursor_pos = Point(cursor_pos.x + 2, cursor_pos.y)
        if input_ch == curses.KEY_UP:
            playsound(sfx_nav_path, block=False)
            cursor_pos = Point(cursor_pos.x, cursor_pos.y - 1)
        if input_ch == curses.KEY_DOWN:
            playsound(sfx_nav_path, block=False)
            cursor_pos = Point(cursor_pos.x, cursor_pos.y + 1)
        if input_ch == curses.KEY_ENTER or input_ch == 10:  # enter
            playsound(sfx_enter_path, block=False)
            game.toggle_mark(*cursor_to_index(cursor_pos, game_rect))
        if input_ch == " " or input_ch == 32:  # spacebar
            playsound(sfx_space_path, block=False)
            game.reveal(*cursor_to_index(cursor_pos, game_rect))
        if input_ch == 27:
            selected = open_menu(curse_context, ("Continue", "New Game", "Exit"))
            if selected == "Exit":
                return
            elif selected == "New Game":
                start_new_game(curse_context)

        if game.is_lost() or game.is_solved():
            playsound(sfx_death_path, block=False)
            game.reveal_all()
            curse_context.clear()
            draw_all(curse_context, game)

            curses.curs_set(False)
            input_ch = curse_context.getch()
            curses.curs_set(True)
            break


def main(curse_context: Any) -> None:
    """Main function called from outside"""
    # curses colours
    curses.init_pair(1, 6, 0)  # 1
    curses.init_pair(2, 4, 0)  # 2
    curses.init_pair(3, 3, 0)  # 3
    curses.init_pair(4, 9, 0)  # 4
    curses.init_pair(5, 1, 0)  # 5+
    curses.init_pair(8, 7, 1)  # mine
    curses.init_pair(9, 0, 3)  # marked

    while True:
        selection = open_menu(
            curse_context, items=("New Game", "Exit"), header="Main Menu"
        )
        if selection == "Exit":
            return  # to load back main menu
        if selection == "New Game":
            start_new_game(curse_context)


if __name__ == "__main__":
    curses.wrapper(main)
    curses.endwin()
