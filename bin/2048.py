import curses
import os
from typing import Any

from twentyfortyeight.components import crsin, crsout, gamectrl


def main(stdscr: Any):
    """Runs the 2048 program."""
    curses.curs_set(0)

    gc = gamectrl.GameController()
    co = crsout.CursesOutput(stdscr, gc)
    ci = crsin.CursesInput(stdscr, gc, co)

    gc.resume_game()

    while gc.is_active():
        ci.get_input()


if __name__ == "__main__":
    # needed for the faster reaction of <ESC> key
    os.environ["ESCDELAY"] = "10"

    curses.wrapper(main)
    curses.endwin()
