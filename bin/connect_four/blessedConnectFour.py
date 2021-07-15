import curses

# import typing

# environment after running demo.py
screen = curses.initscr()
curses.cbreak()
screen.keypad(1)
curses.noecho()
curses.curs_set(1)


class ConnectFour:
    """A two-player connect four game.

    It plays the logo & title screen once and initialises
    the board size each run of the game.
    """

    import time

    import numpy as np
    import text_arts as ta
    from blessed import Terminal

    tm = Terminal()
    sty_default = tm.bright_white_on_blue2
    sty_p1 = tm.bright_yellow_on_blue2
    sty_p2 = tm.coral1_on_blue2
    hgt = tm.height
    wth = tm.width

    if hgt < 11 or wth < 60:
        TITLE_TXT = ta.TITLE_S
        LOGO_TXT = ta.LOGO_S
        NAME_TXT = ta.NAME_S
    elif hgt < 24 or wth < 80:
        TITLE_TXT = ta.TITLE_M
        LOGO_TXT = ta.LOGO_M
        NAME_TXT = ta.NAME_M
    else:
        TITLE_TXT = ta.TITLE_L
        LOGO_TXT = ta.LOGO_L
        NAME_TXT = ta.NAME_L

    min_nRow_nCol = 0
    max_nCol = min(26, wth // 4 - 1)
    max_nRow = hgt // 4
    COL_SYMS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    ################################################################
    with tm.cbreak(), tm.hidden_cursor():
        # clear the screen
        print(tm.home + sty_default + tm.clear)

        for i in range(len(LOGO_TXT)):
            logo_part = (
                tm.move_xy(
                    wth // 2 - len(LOGO_TXT[0]) // 2,
                    (hgt // 4 - len(LOGO_TXT) // 4) + i,
                )
                + LOGO_TXT[i]
            )
            print(logo_part, end="", flush=True)
        for i in range(len(NAME_TXT)):
            logo_part = (
                tm.move_xy(
                    wth // 2 - len(NAME_TXT[0]) // 2,
                    (hgt // 4 - len(LOGO_TXT) // 4) + 2 + len(LOGO_TXT) + i,
                )
                + NAME_TXT[i]
            )
            print(logo_part, end="", flush=True)
        time.sleep(3.5)
        print(tm.home + sty_default + tm.clear)

        for i in range(len(TITLE_TXT)):
            title_part = (
                tm.move_xy(
                    wth // 2 - len(TITLE_TXT[0]) // 2,
                    hgt // 2 - len(TITLE_TXT) // 2 + i,
                )
                + TITLE_TXT[i]
            )
            print(title_part, end="", flush=True)

        start_txt = False
        start = tm.move_xy(wth // 2 - 8, hgt * 3 // 4) + "Press S to start"
        start_ers = tm.move_xy(wth // 2 - 8, hgt * 3 // 4) + 16 * " "
        while tm.inkey(timeout=0.75) != "s":
            if not start_txt:
                print(start, end="", flush=True)
                start_txt = True
            else:
                print(start_ers, end="", flush=True)
                start_txt = False

    print(tm.home + tm.clear)

    ################################################################
    def __init__(self):
        """Initialises board size"""
        print(self.tm.home + self.tm.clear)
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        self.nrow, self.ncol = self.get_nrow_ncol()
        curses.cbreak()
        screen.keypad(1)
        curses.noecho()
        self.avail_choices = set(range(self.ncol))
        self.mx = self.np.zeros((self.nrow, self.ncol), self.np.int8)

    def get_nrow_ncol(self) -> (int, int):
        """Get a user input for board size"""
        nrow, ncol = None, None
        size_prpt = (
            self.tm.move_xy(self.wth // 2 - 26, self.hgt // 3)
            + "Please enter the size of the board as HEIGHT x WIDTH.\n"
        )
        print(size_prpt, end="", flush=True)
        size_pd = self.tm.move_y(self.hgt // 2) + f"\n{' '*(self.wth//2-2)}"

        while True:
            try:
                print(size_pd, end="", flush=True)
                nrow, ncol = input("").split("x", 2)
            except ValueError:
                error = (
                    self.tm.move_xy(self.wth // 2 - 18, self.hgt // 3)
                    + "Please use the format HEIGHT x WIDTH."
                )
                print(self.tm.home + self.tm.clear)
                print(error, end="", flush=True)
                continue
            try:
                nrow, ncol = int(nrow), int(ncol)
            except ValueError:
                error = (
                    self.tm.move_xy(self.wth // 2 - 22, self.hgt // 3)
                    + "Both height and width must be integer values."
                )
                nrow, ncol = None, None
                print(self.tm.home + self.tm.clear)
                print(error, end="", flush=True)
                continue
            except TypeError:
                error = (
                    self.tm.move_xy(self.wth // 2 - 18, self.hgt // 3)
                    + "Please use the format HEIGHT x WIDTH."
                )
                nrow, ncol = None, None
                print(self.tm.home + self.tm.clear)
                print(error, end="", flush=True)
                continue
            if nrow < self.min_nRow_nCol or ncol < self.min_nRow_nCol:
                error = (
                    self.tm.move_xy(self.wth // 2 - 20, self.hgt // 3)
                    + "Both height and width "
                    + f"must be at least {self.min_nRow_nCol}."
                )
                nrow, ncol = None, None
                print(self.tm.home + self.tm.clear)
                print(error, end="", flush=True)
                continue
            elif ncol > self.max_nCol:
                error = (
                    self.tm.move_xy(self.wth // 2 - 15, self.hgt // 3)
                    + f"Width must be no more than {self.max_nCol}."
                )
                nrow, ncol = None, None
                print(self.tm.home + self.tm.clear)
                print(error, end="", flush=True)
                continue
            elif nrow > self.max_nRow:
                error = (
                    self.tm.move_xy(self.wth // 2 - 15, self.hgt // 3)
                    + f"Height must be no more than {self.max_nRow}."
                )
                nrow, ncol = None, None
                print(self.tm.home + self.tm.clear)
                print(error, end="", flush=True)
                continue
            else:
                break
        return nrow, ncol

    def start(self) -> bool:
        """Plays game of set size"""
        print(self.tm.home + self.tm.clear)
        cur_player = 1
        end = False
        number_of_moves = 0
        total_moves = self.nrow * self.ncol

        head_row_txt = f"  {self.COL_SYMS[0]}"
        for i in range(1, self.ncol):
            head_row_txt += f"   {self.COL_SYMS[i]}"
        head_row = (
            self.tm.move_xy(
                self.wth // 2 - (self.ncol * 4 + 1) // 2,
                self.hgt // 4,
            )
            + head_row_txt
        )
        print(head_row, end="", flush=True)

        for i in range(self.nrow):
            body_row_txt = ""  # * (self.wth // 2 - (self.ncol * 4 + 1) // 2)
            for j in range(self.ncol):
                body_row_txt += f"│ {self.mx[i][j]} "
            body_row_txt += "│\n"
            body_row = (
                self.tm.move_xy(
                    self.wth // 2 - (self.ncol * 4 + 1) // 2,
                    self.hgt // 4 + 1 + i,
                )
                + body_row_txt
            )
            print(body_row, end="", flush=True)

        foot_row_txt = "⎺" * (self.ncol * 4 + 1)
        # + "" * (self.wth // 2 - (self.ncol * 4 + 1) // 2) + \

        foot_row = (
            self.tm.move_xy(
                self.wth // 2 - (self.ncol * 4 + 1) // 2,
                self.hgt // 4 + self.nrow + 1,
            )
            + foot_row_txt
        )
        print(foot_row, end="", flush=True)

        prpt_pd = self.hgt // 4 + self.nrow + 3
        prpt1_p1 = (
            self.tm.move_xy(self.wth // 2 - 8, prpt_pd)
            + f"Player {self.sty_p1('1')+self.sty_default}'s turn."
        )
        prpt1_p2 = (
            self.tm.move_xy(self.wth // 2 - 8, prpt_pd)
            + f"Player {self.sty_p2('2')+self.sty_default}'s turn."
        )
        prpt1_win1 = (
            self.tm.move_xy(self.wth // 2 - 8, prpt_pd)
            + f"Player {self.sty_p1('1') + self.sty_default} has won!"
        )
        prpt1_win2 = (
            self.tm.move_xy(self.wth // 2 - 8, prpt_pd)
            + f"Player {self.sty_p2('2') + self.sty_default} has won!"
        )
        prpt1_draw = self.tm.move_xy(self.wth // 2 - 2, prpt_pd) + "Draw!"
        prpt1_ers = self.tm.move_xy(self.wth // 2 - 8, prpt_pd) + 18 * " "

        last_col = self.COL_SYMS[self.ncol - 1]
        prpt2 = (
            self.tm.move_xy(self.wth // 2 - 18, prpt_pd + 2)
            + "Choose a column by typing its letter."
        )
        prpt2_error = (
            self.tm.move_xy(self.wth // 2 - 21, prpt_pd + 2)
            + f"Invalid column. Choose a column from A to {last_col}"
        )
        prpt2_full = (
            self.tm.move_xy(self.wth // 2 - 23, prpt_pd + 2)
            + f"Column is full. Choose a column from A to {last_col}"
        )
        prpt2_ers = self.tm.move_xy(self.wth // 2 - 23, prpt_pd + 2) + 47 * " "
        prpt2_end = (
            self.tm.move_xy(self.wth // 2 - 18, prpt_pd + 2)
            + "Press R to restart, press Q to quit."
        )

        with self.tm.cbreak(), self.tm.hidden_cursor():
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
                        choice_sym = self.tm.inkey(timeout=0.5)
                        if not choice_sym:
                            continue
                        choice = int(self.COL_SYMS.index(choice_sym.upper()))
                    except ValueError:
                        print(prpt2_error, end="", flush=True)
                        continue
                    valid = self.check_choice(choice, prpt2_error, prpt2_full)

                if cur_player == 1:
                    print(prpt1_ers + prpt1_p2, end="", flush=True)
                else:
                    print(prpt1_ers + prpt1_p1, end="", flush=True)
                print(prpt2_ers + prpt2, end="", flush=True)
                row = self.drop(cur_player, choice)

                number_of_moves += 1
                if self.check_win(cur_player, choice, row):
                    if cur_player == 1:
                        print(prpt1_win1, end="", flush=True)
                    else:
                        print(prpt1_win2, end="", flush=True)
                    end = True
                if number_of_moves == total_moves:
                    print(prpt1_ers + prpt1_draw, end="", flush=True)
                    end = True
                # Switch players
                if cur_player == 1:
                    cur_player = 2
                else:
                    cur_player = 1

            print(prpt2_ers + prpt2_end, end="", flush=True)
            while True:
                choice_sym = self.tm.inkey(timeout=0.5)
                if choice_sym == "r":
                    return True
                if choice_sym == "q":
                    print(
                        f"\n\n\n\n{' '*(self.wth//2-16)}"
                        + "GAME ENDED. RETURN TO MAIN MENU.\n\n\n"
                    )
                    return False

    def col_full(self, col: int) -> bool:
        """Check if a chosen column is full"""
        for i in range(self.nrow):
            if self.mx[i][col] == 0:
                return False
        return True

    def check_choice(self, choice: int, prpt2_error: str, prpt2_full: str) -> bool:
        """Check if a chosen column is within the board"""
        if choice not in self.avail_choices:
            print(prpt2_error, end="", flush=True)
            return False
        if self.col_full(choice):
            print(prpt2_full, end="", flush=True)
            return False
        return True

    def drop(self, cur_player: int, col: int) -> int:
        """Drops a disc in a column"""
        for i in range(self.nrow):
            self.time.sleep(0.15)
            if cur_player == 1:
                disc_text = self.sty_p1("1")
            else:
                disc_text = self.sty_p2("2")
            disc = (
                self.tm.move_xy(
                    self.wth // 2 - (self.ncol * 4 + 1) // 2 + 2 + 4 * col,
                    self.hgt // 4 + 1 + i,
                )
                + disc_text
            )
            disc_ers = (
                self.tm.move_xy(
                    self.wth // 2 - (self.ncol * 4 + 1) // 2 + 2 + 4 * col,
                    self.hgt // 4 + i,
                )
                + self.sty_default("0")
            )
            if self.mx[i][col] == 0:
                print(disc)
                if i > 0:
                    print(disc_ers)
            else:
                break
        for i in reversed(range(self.nrow)):
            if self.mx[i][col] == 0:
                self.mx[i][col] = cur_player
                break
        print(self.sty_default)
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
        dg = self.np.diag(self.mx, col - row)
        for i in dg:
            if i == cur_player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0

        # right diagonal
        count = 0
        dg = self.np.diag(self.np.fliplr(self.mx), (self.ncol - 1 - col) - row)
        for i in dg:
            if i == cur_player:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0


if __name__ == "__main__":
    play = True
    while play:
        connectFour = ConnectFour()
        play = connectFour.start()
