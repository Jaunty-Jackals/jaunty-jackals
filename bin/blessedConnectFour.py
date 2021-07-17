import curses
import time

import ConnectFour.sound_paths as sp
import ConnectFour.text_arts as ta
import numpy as np
from blessed import Terminal
from play_sounds import play_file as play_sfx
from play_sounds import play_while_running as play_bgm

# environment after running demo.py
screen = curses.initscr()
curses.cbreak()
screen.keypad(1)
curses.noecho()
curses.curs_set(1)

tm = Terminal()
HGT = tm.height
WTH = tm.width

STY_DEF = tm.bright_white_on_black
STY_ESC = tm.black_on_deepskyblue
STY_COL = tm.deepskyblue_on_black
STY_P1 = tm.gold_on_black
STY_P2 = tm.tomato_on_black

if HGT < 11 or WTH < 60:
    TITLE_TXT = ta.TITLE_S
    LOGO_TXT = ta.LOGO_S
    NAME_TXT = ta.NAME_S
elif HGT < 24 or WTH < 80:
    TITLE_TXT = ta.TITLE_M
    LOGO_TXT = ta.LOGO_M
    NAME_TXT = ta.NAME_M
else:
    TITLE_TXT = ta.TITLE_L
    LOGO_TXT = ta.LOGO_L
    NAME_TXT = ta.NAME_L

MIN_NROW_NCOL = 0
MAX_NCOL = min(26, WTH // 4 - 1)
MAX_NROW = HGT // 4
COL_SYMS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class ConnectFour:
    """A two-player connect four game.

    The ConnectFour class, class functions and algorithm are 
    taken from ConnectFour by AlexZzander (https://github.com/AlexZzander/ConnectFour).
    TUI features and function modifications are completed by vguo2037.
    """

    def __init__(self):
        """Initialises board size"""
        print(tm.home + STY_DEF + tm.clear)

        with tm.cbreak(), tm.hidden_cursor():
            # clear the screen
            print(tm.home + STY_DEF + tm.clear)

            for i in range(len(LOGO_TXT)):
                logo_part = (
                    tm.move_xy(
                        WTH // 2 - len(LOGO_TXT[0]) // 2,
                        (HGT // 4 - len(LOGO_TXT) // 4) + i,
                    )
                    + LOGO_TXT[i]
                )
                print(logo_part, end="", flush=True)
            for i in range(len(NAME_TXT)):
                logo_part = (
                    tm.move_xy(
                        WTH // 2 - len(NAME_TXT[0]) // 2,
                        (HGT // 4 - len(LOGO_TXT) // 4) + 2 + len(LOGO_TXT) + i,
                    )
                    + NAME_TXT[i]
                )
                print(logo_part, end="", flush=True)
            time.sleep(3.5)

            print(tm.home + STY_DEF + tm.clear)

            for i in range(len(TITLE_TXT)):
                title_part = (
                    tm.move_xy(
                        WTH // 2 - len(TITLE_TXT[0]) // 2,
                        HGT // 2 - len(TITLE_TXT) // 2 + i,
                    )
                    + TITLE_TXT[i]
                )
                print(title_part, end="", flush=True)

            start_txt = False
            start = tm.move_xy(WTH // 2 - 8, HGT * 3 // 4) + "Press S to start"
            start_ers = tm.move_xy(WTH // 2 - 8, HGT * 3 // 4) + 16 * " "
            while tm.inkey(timeout=0.75) != "s":
                if not start_txt:
                    print(start, end="", flush=True)
                    start_txt = True
                else:
                    print(start_ers, end="", flush=True)
                    start_txt = False
            play_sfx(sp.drop, block=False)

        print(tm.home + STY_DEF + tm.clear)
        self.nrow, self.ncol = self.get_nrow_ncol()
        self.avail_choices = set(range(self.ncol))
        self.mx = np.zeros((self.nrow, self.ncol), np.int8)

    def get_nrow_ncol(self) -> (int, int):
        """Get a user input for board size"""
        nrow, ncol = None, None
        size_prpt = (
            tm.move_xy(WTH // 2 - 26, HGT // 3)
            + "Please enter the size of the board as HEIGHT x WIDTH.\n"
        )
        print(size_prpt, end="", flush=True)
        size_pd = tm.move_xy(WTH // 2 - 2, HGT // 2)

        while True:
            print(size_prpt + size_pd, end="", flush=True)
            try:
                size_input = ""
                while True:
                    choice_sym = tm.inkey(timeout=0.25)
                    if not choice_sym:
                        continue
                    elif choice_sym == chr(13):
                        break
                    elif choice_sym in [chr(8), chr(127)]:
                        size_input = size_input[:-1]
                        mod_size_pd = tm.move_xy(
                            WTH // 2 - 2 + len(size_input), HGT // 2
                        )
                        print(mod_size_pd + " " + mod_size_pd, end="", flush=True)
                    elif choice_sym.isdigit() or choice_sym in " x":
                        print(choice_sym, end="", flush=True)
                        size_input += choice_sym
                nrow, ncol = size_input.split("x", 2)
            except ValueError:
                size_prpt = (
                    tm.move_xy(WTH // 2 - 18, HGT // 3)
                    + "Please use the format HEIGHT x WIDTH."
                )
                play_sfx(sp.badcol, block=False)
                print(tm.home + STY_DEF + tm.clear, end="", flush=True)
                continue
            try:
                nrow, ncol = int(nrow), int(ncol)
            except ValueError:
                size_prpt = (
                    tm.move_xy(WTH // 2 - 22, HGT // 3)
                    + "Both height and width must be integer values."
                )
                nrow, ncol = None, None
                play_sfx(sp.badcol, block=False)
                print(tm.home + STY_DEF + tm.clear, end="", flush=True)
                continue
            except TypeError:
                size_prpt = (
                    tm.move_xy(WTH // 2 - 18, HGT // 3)
                    + "Please use the format HEIGHT x WIDTH."
                )
                nrow, ncol = None, None
                play_sfx(sp.badcol, block=False)
                print(tm.home + STY_DEF + tm.clear, end="", flush=True)
                continue
            if nrow < MIN_NROW_NCOL or ncol < MIN_NROW_NCOL:
                size_prpt = (
                    tm.move_xy(WTH // 2 - 20, HGT // 3)
                    + "Both height and width "
                    + f"must be at least {MIN_NROW_NCOL}."
                )
                nrow, ncol = None, None
                play_sfx(sp.badcol, block=False)
                print(tm.home + STY_DEF + tm.clear, end="", flush=True)
                continue
            elif ncol > MAX_NCOL:
                size_prpt = (
                    tm.move_xy(WTH // 2 - 15, HGT // 3)
                    + f"Width must be no more than {MAX_NCOL}."
                )
                nrow, ncol = None, None
                play_sfx(sp.badcol, block=False)
                print(tm.home + STY_DEF + tm.clear, end="", flush=True)
                continue
            elif nrow > MAX_NROW:
                size_prpt = (
                    tm.move_xy(WTH // 2 - 15, HGT // 3)
                    + f"Height must be no more than {MAX_NROW}."
                )
                nrow, ncol = None, None
                play_sfx(sp.badcol, block=False)
                print(tm.home + STY_DEF + tm.clear, end="", flush=True)
                continue
            else:
                break
        play_sfx(sp.drop, block=False)
        return nrow, ncol

    def print_board(self):
        """Prints the playing screen"""
        print(tm.home + STY_DEF + tm.clear)
        print("   " + STY_ESC + "ESC" + STY_DEF + " Pause")

        head_row_txt = f"  {COL_SYMS[0]}"
        for i in range(1, self.ncol):
            head_row_txt += f"   {COL_SYMS[i]}"
        head_row = (
            tm.move_xy(
                WTH // 2 - (self.ncol * 4 + 1) // 2,
                HGT // 4,
            )
            + head_row_txt
        )
        print(STY_COL + head_row + STY_DEF, end="", flush=True)

        for i in range(self.nrow):
            body_row_txt = ""  # * (WTH // 2 - (self.ncol * 4 + 1) // 2)
            for j in range(self.ncol):
                body_row_txt += (STY_COL + f"│ {STY_DEF + str(self.mx[i][j])} ")
            body_row_txt += STY_COL + "│\n" + STY_DEF
            body_row = (
                tm.move_xy(
                    WTH // 2 - (self.ncol * 4 + 1) // 2,
                    HGT // 4 + 1 + i,
                )
                + body_row_txt
            )
            print(body_row, end="", flush=True)

        foot_row_txt = "⎺" * (self.ncol * 4 + 1)
        # + "" * (WTH // 2 - (self.ncol * 4 + 1) // 2) + \

        foot_row = (
            tm.move_xy(
                WTH // 2 - (self.ncol * 4 + 1) // 2,
                HGT // 4 + self.nrow + 1,
            )
            + foot_row_txt
        )
        print(STY_COL + foot_row + STY_DEF, end="", flush=True)

    def start(self) -> bool:
        """Plays game of set size"""
        cur_player = 1
        end = False
        number_of_moves = 0
        total_moves = self.nrow * self.ncol

        prpt_pd = HGT // 4 + self.nrow + 3
        prpt1_p1 = (
            tm.move_xy(WTH // 2 - 8, prpt_pd) + f"Player {STY_P1('1')+STY_DEF}'s turn."
        )
        prpt1_p2 = (
            tm.move_xy(WTH // 2 - 8, prpt_pd) + f"Player {STY_P2('2')+STY_DEF}'s turn."
        )
        prpt1_wn1 = (
            tm.move_xy(WTH // 2 - 8, prpt_pd)
            + f"Player {STY_P1('1') + STY_DEF} has won!"
        )
        prpt1_wn2 = (
            tm.move_xy(WTH // 2 - 8, prpt_pd)
            + f"Player {STY_P2('2') + STY_DEF} has won!"
        )
        prpt1_drw = tm.move_xy(WTH // 2 - 2, prpt_pd) + "Draw!"
        prpt1_esc = tm.move_xy(WTH // 2 - 6, prpt_pd) + "Game paused."
        prpt1_ers = tm.move_xy(WTH // 2 - 8, prpt_pd) + 18 * " "

        last_col = COL_SYMS[self.ncol - 1]
        prpt2 = (
            tm.move_xy(WTH // 2 - 18, prpt_pd + 2)
            + "Choose a column by typing its letter."
        )
        prpt2_err = (
            tm.move_xy(WTH // 2 - 21, prpt_pd + 2)
            + f"Invalid column. Choose a column from A to {last_col}"
        )
        prpt2_ful = (
            tm.move_xy(WTH // 2 - 23, prpt_pd + 2)
            + f"Column is full. Choose a column from A to {last_col}"
        )
        prpt2_esc = (
            tm.move_xy(WTH // 2 - 30, prpt_pd + 2)
            + "Press ESC again to quit, R to restart, or RETURN to continue."
        )
        prpt2_end = (
            tm.move_xy(WTH // 2 - 18, prpt_pd + 2)
            + "Press R to restart, press Q to quit."
        )
        prpt2_ers = tm.move_xy(WTH // 2 - 31, prpt_pd + 2) + 62 * " "

        self.print_board()

        with tm.cbreak(), tm.hidden_cursor():
            print()
            print()
            if cur_player == 1:
                print(prpt1_ers + prpt1_p1, end="", flush=True)
            else:
                print(prpt1_ers + prpt1_p2, end="", flush=True)
            print(prpt2_ers + prpt2, end="", flush=True)
            while not end:
                valid = False

                while not valid:
                    try:
                        choice_sym = tm.inkey(timeout=0.5)
                        if not choice_sym:
                            continue
                        elif choice_sym == chr(27):
                            print(
                                prpt1_ers + prpt1_esc + prpt2_ers + prpt2_esc,
                                end="",
                                flush=True,
                            )
                            while True:
                                choice_sym = tm.inkey(timeout=0.5)
                                if not choice_sym:
                                    continue
                                elif choice_sym == chr(13):
                                    # press RETURN to continue
                                    if cur_player == 1:
                                        print(prpt1_ers + prpt1_p1, end="", flush=True)
                                    else:
                                        print(prpt1_ers + prpt1_p2, end="", flush=True)
                                    break
                                elif choice_sym == "r":
                                    # press R to restart
                                    return True
                                elif choice_sym == chr(27):
                                    # press ESC to quit
                                    return False
                        choice = int(COL_SYMS.index(choice_sym.upper()))

                    except ValueError:
                        print(prpt2_ers + prpt2_err, end="", flush=True)
                        play_sfx(sp.badcol, block=False)
                        continue
                    valid = self.check_choice(choice, prpt2_ers, prpt2_err, prpt2_ful)

                row = self.drop(cur_player, choice)
                if cur_player == 1:
                    print(prpt1_ers + prpt1_p2, end="", flush=True)
                else:
                    print(prpt1_ers + prpt1_p1, end="", flush=True)
                print(prpt2_ers + prpt2, end="", flush=True)

                number_of_moves += 1
                if self.check_win(cur_player, choice, row):
                    play_sfx(sp.win, block=False)
                    if cur_player == 1:
                        print(prpt1_wn1, end="", flush=True)
                    else:
                        print(prpt1_wn2, end="", flush=True)
                    end = True
                if number_of_moves == total_moves:
                    print(prpt1_ers + prpt1_drw, end="", flush=True)
                    end = True
                # Switch players
                if cur_player == 1:
                    cur_player = 2
                else:
                    cur_player = 1

            print(prpt2_ers + prpt2_end, end="", flush=True)
            while True:
                choice_sym = tm.inkey(timeout=0.5)
                if choice_sym == "r":
                    return True
                if choice_sym == "q":
                    return False

    def col_full(self, col: int) -> bool:
        """Check if a chosen column is full"""
        for i in range(self.nrow):
            if self.mx[i][col] == 0:
                return False
        return True

    def check_choice(self, choice: int, p_ers: str, p_err: str, p_ful: str) -> bool:
        """Check if a chosen column is within the board"""
        if choice not in self.avail_choices:
            print(p_ers + p_err, end="", flush=True)
            play_sfx(sp.badcol, block=False)
            return False
        if self.col_full(choice):
            print(p_ers + p_ful, end="", flush=True)
            play_sfx(sp.badcol, block=False)
            return False
        return True

    def drop(self, cur_player: int, col: int) -> int:
        """Drops a disc in a column"""
        for i in range(self.nrow):
            choice_sym = tm.inkey(0.01)
            # just to use choice_sym somehow so flake8 is happy
            if choice_sym:
                pass
            time.sleep(0.067)
            if cur_player == 1:
                disc_text = STY_P1("1")
            else:
                disc_text = STY_P2("2")
            disc = (
                tm.move_xy(
                    WTH // 2 - (self.ncol * 4 + 1) // 2 + 2 + 4 * col,
                    HGT // 4 + 1 + i,
                )
                + disc_text
            )
            disc_ers = (
                tm.move_xy(
                    WTH // 2 - (self.ncol * 4 + 1) // 2 + 2 + 4 * col,
                    HGT // 4 + i,
                )
                + STY_DEF("0")
            )
            if self.mx[i][col] == 0:
                print(disc)
                play_sfx(sp.boop, block=False)
                if i > 0:
                    print(disc_ers)
            else:
                break
        for i in reversed(range(self.nrow)):
            if self.mx[i][col] == 0:
                self.mx[i][col] = cur_player
                break
        play_sfx(sp.drop, block=False)
        print(STY_DEF)
        return i

    def check_win(self, cur_player: int, col: int, row: int) -> bool:
        """Check if a player has won"""
        count = 0
        for i in range(self.ncol):
            if self.mx[row][i] == cur_player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0

        # vertical
        count = 0
        for i in range(self.nrow):
            if self.mx[i][col] == cur_player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0

        # left diagonal
        count = 0
        dg = np.diag(self.mx, col - row)
        for i in dg:
            if i == cur_player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0

        # right diagonal
        count = 0
        dg = np.diag(np.fliplr(self.mx), (self.ncol - 1 - col) - row)
        for i in dg:
            if i == cur_player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0


if __name__ == "__main__":
    play = True
    with play_bgm(sp.bgm, block=True):
        while play:
            time.sleep(0.5)
            connectFour = ConnectFour()
            play = connectFour.start()
    print(
        tm.home
        + tm.clear
        + tm.move_xy(WTH // 2 - 12, HGT // 2)
        + "Returning to main menu..."
    )
    time.sleep(1)
