#!/usr/bin/env python3

import components.gamectrl
import components.crsout
import components.crsin

import curses
import os

def main(stdscr):
    curses.curs_set(0)

    gc = components.gamectrl.GameController()
    co = components.crsout.CursesOutput(stdscr, gc)
    ci = components.crsin.CursesInput(stdscr, gc, co)

    gc.resume_game()

    while(gc.is_active()):
        ci.get_input()

if __name__ == "__main__":
    # needed for the faster reaction of <ESC> key
    os.environ["ESCDELAY"] = "10"

    curses.wrapper(main)
