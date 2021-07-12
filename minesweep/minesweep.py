#!/usr/bin/python3.9

import curses
import random
from collections import namedtuple
from enum import Enum
from math import sqrt
from utils import open_menu, draw_rect, minmax, Rect


class Flags(Enum):
    INITIAL = 0
    MARKED = 1
    REVEALED = 2


class MineSweeper:
    def __init__(self, mines, flags=None):
        if flags is None:
            flags = Table(mines.num_cols, mines.num_rows, Flags.INITIAL)
        if mines.size() != flags.size():
            raise ValueError('Fields cannot have different sizes ({0} != {1})'.format(mines.size(), flags.size()))
        self.mines = mines
        self.flags = flags
        self.hints = Table(mines.num_cols, mines.num_rows, 0)

        for i, _ in enumerate(self.hints):
            self.hints[i] = self.hint(*self.hints.linear_to_subscript(i))

    def rows(self):
        return self.mines.num_rows

    def columns(self):
        return self.mines.num_cols

    def hint(self, x, y):
        if self.mines[x, y]:
            return -1
        else:
            h = 0
            for a, b in self.mines.neighbours(x, y):
                if(self.mines[a, b]):
                    h += 1
            return h

    def is_solved(self):
        for mine, flag in zip(self.mines, self.flags):
            if mine and flag != Flags.MARKED:
                return False
        return True

    def is_lost(self):
        for mine, flag in zip(self.mines, self.flags):
            if mine and flag == Flags.REVEALED:
                return True
        return False

    def auto_mark(self):
        for mine, flag in zip(self.mines, self.flags):
            if not mine and flag != Flags.REVEALED:
                return False

        for i, mine in enumerate(self.mines):
            if mine:
                self.flags[i] = Flags.MARKED
            else:
                self.flags[i] = Flags.REVEALED

    def reveal_all(self):
        for i, flag in enumerate(self.flags):
            if flag != Flags.MARKED:
                self.flags[i] = Flags.REVEALED

    def reveal(self, x, y, reveal_known=True):
        if self.flags[x, y] == Flags.MARKED:
            self.flags[x, y] = Flags.INITIAL
        elif self.flags[x, y] == Flags.REVEALED:
            if self.hints[x, y] <= 0 or not reveal_known:
                return True
            neighbours = list(self.mines.neighbours(x, y))
            neighbour_mines = [(nx, ny) for nx, ny in neighbours if self.flags[nx, ny] == Flags.MARKED]
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
                            ok = self.reveal(nx, ny, reveal_known=False)
                            assert ok
                self.auto_mark()
        return True

    def toggle_mark(self, x, y):
        if self.flags[x, y] == Flags.INITIAL:
            self.flags[x, y] = Flags.MARKED
        elif self.flags[x, y] == Flags.MARKED:
            self.flags[x, y] = Flags.INITIAL
        self.auto_mark()

    def print_field(self):
        s = ''
        for y in range(self.mines.num_rows):
            for x in range(self.mines.num_cols):
                f, m = self.flags[x, y], self.mines[x, y]
                if f == Flags.INITIAL:
                    s += '?'
                elif f == Flags.MARKED:
                    s += '!'
                elif f == Flags.REVEALED:
                    if m:
                        s += '*'
                    else:
                        s += str(self.hint(x, y))
            s += '\n'
        print(s)

    @classmethod
    def create_random(cls, cols, rows, num_mines):
        mines = Table(cols, rows, False)
        flags = Table(cols, rows, Flags.INITIAL)

        fields = [(c, r) for c in range(cols) for r in range(rows)]
        for x, y in random.sample(fields, num_mines):
            mines[x, y] = True
        return MineSweeper(mines, flags)


class Table:
    def __init__(self, cols, rows, default=0):
        if (cols <= 0) or (rows <= 0):
            raise ValueError('Invalid rows/cols provided for table')
        self.table = [default for c in range(cols * rows)]
        self.num_cols = cols
        self.num_rows = rows

    def size(self):
        return self.num_cols * self.num_rows

    def __getitem__(self, key):
        try:
            x, y = key
            if x >= self.num_cols or y >= self.num_rows:
                raise IndexError('list index out of range')
            return self.table[self.subscript_to_linear(x, y)]
        except TypeError:
            return self.table[key]

    def __setitem__(self, key, value):
        try:
            x, y = key
            if x >= self.num_cols or y >= self.num_rows:
                raise IndexError('list index out of range')
            self.table[self.subscript_to_linear(x, y)] = value
        except TypeError:
            self.table[key] = value

    def neighbours(self, x, y):
        for c in range(max(x-1, 0), min(x+2, self.num_cols)):
            for r in range(max(y-1, 0), min(y+2, self.num_rows)):
                if c != x or r != y:
                    yield(c, r)

    def linear_to_subscript(self, index):
        return (index % self.num_cols, index // self.num_cols)

    def subscript_to_linear(self, col, row):
        return col + row*self.num_cols

    def count(self, value):
        return self.table.count(value)

    def row(self, r):
        start = self.subscript_to_linear(0, r)
        return self.table[start: start + self.num_cols]

    def __iter__(self):
        for y in range(self.num_rows):
            for x in range(self.num_cols):
                yield self[x, y]


def start_new_game(curse_context):
    boxes = int(open_menu(curse_context, items=("100", "400", "625"), header="Number of Boxes"))
    mine_percents = [0.1, 0.2, 0.4, 0.6]
    mines = [str(int(boxes * mp)) for mp in mine_percents]
    sel_mines = int(float(open_menu(curse_context, items=tuple(mines), header="Number of Mines")))

    final_cols = int(minmax(sqrt(boxes), 0, curses.COLS-3))
    final_rows = int(minmax(sqrt(boxes), 0, curses.LINES-5))

    start_game(curse_context, final_cols, final_rows, sel_mines)


def cursor_to_index(cursor_pos, game_rect):
    return ((cursor_pos.x - game_rect.x)//2, cursor_pos.y - game_rect.y)


def main(curse_context):
    while True:
        selection = open_menu(curse_context, items=("New Game", "Exit"), header="Main Menu")
        if selection == "Exit":
            return  # to load back main menu
        if selection == "New Game":
            start_new_game(curse_context)


def get_header(curse_context, game):
    if game.is_solved():
        text = "Congratulations, You Won!"
    elif game.is_lost():
        text = "You Lost!"
    else:
        remaining = game.mines.count(True) - game.flags.count(Flags.MARKED)
        text = "Remaining Mines: {0}".format(remaining)
    curse_context.addstr(0, 0, text, curses.A_REVERSE)
    return Rect(0, 0, curses.COLS-1, 1)


def get_footer(curse_context, game):
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
        curse_context.addstr(curses.LINES-1, offset, name, curses.A_REVERSE)
        offset += len(name)
        curse_context.addstr(curses.LINES-1, offset, " " + control + " ")
        offset += len(control) + 2
    return Rect(0, curses.LINES-1, curses.COLS-1, 1)


def get_game(curse_context, game, game_rect):
    rect = Rect(game_rect.x, game_rect.y, game.columns()*2+1, game.rows()+2)
    rect = draw_rect(curse_context, rect)

    for i, (mine, flag, hint) in enumerate(zip(game.mines, game.flags, game.hints)):
        x, y = game.mines.linear_to_subscript(i)
        x = x*2 + rect.x
        y = y + rect.y
        if flag == Flags.INITIAL:
            curse_context.addstr(y, x, "?")
        elif flag == Flags.MARKED:
            curse_context.addstr(y, x, "\u26F3")
        else:
            if mine:
                curse_context.addstr(y, x, "\u26ED")
            else:
                if hint == 0:
                    curse_context.addstr(y, x, " ")
                else:
                    curse_context.addstr(y, x, str(hint), curses.A_DIM)
    return rect


def draw_all(curse_context, game):
    game_head = get_header(curse_context, game)
    game_foot = get_footer(curse_context, game)
    game_body = Rect(0, game_head.height, curses.COLS-1, curses.LINES-1-game_head.height-game_foot.height)
    full_game = get_game(curse_context, game, game_body)
    return full_game


def start_game(curse_context, cols, rows, mines):
    game = MineSweeper.create_random(cols, rows, mines)

    Point = namedtuple('Point', ['x', 'y'])
    cursor_pos = Point(0, 0)

    while True:
        curse_context.clear()
        game_rect = draw_all(curse_context, game)

        cursor_pos = Point(
            minmax(cursor_pos.x, game_rect.x, game_rect.x+game_rect.width-1),
            minmax(cursor_pos.y, game_rect.y, game_rect.y+game_rect.height-1)
        )
        curse_context.move(cursor_pos.y, cursor_pos.x)
        curse_context.refresh()

        input_ch = curse_context.getch()
        if input_ch == curses.KEY_LEFT:
            cursor_pos = Point(cursor_pos.x-2, cursor_pos.y)
        if input_ch == curses.KEY_RIGHT:
            cursor_pos = Point(cursor_pos.x+2, cursor_pos.y)
        if input_ch == curses.KEY_UP:
            cursor_pos = Point(cursor_pos.x, cursor_pos.y-1)
        if input_ch == curses.KEY_DOWN:
            cursor_pos = Point(cursor_pos.x, cursor_pos.y+1)
        if input_ch == curses.KEY_ENTER or input_ch == 10:
            game.toggle_mark(*cursor_to_index(cursor_pos, game_rect))
        if input_ch == " " or input_ch == 32:
            game.reveal(*cursor_to_index(cursor_pos, game_rect))
        if input_ch == 27:
            selected = open_menu(curse_context, ("Continue", "New Game", "Exit"))
            if selected == "Exit":
                return
            elif selected == "New Game":
                start_new_game(curse_context)

        if game.is_lost() or game.is_solved():
            game.reveal_all()
            curse_context.clear()
            draw_all(curse_context, game)

            curses.curs_set(False)
            input_ch = curse_context.getch()
            curses.curs_set(True)
            break


if __name__ == "__main__":
    curses.wrapper(main)
