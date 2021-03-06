"""Snake."""

import curses
import multiprocessing
import secrets
import time
from platform import system
from typing import Any

from minesweep.minesweep_utils import open_menu
from play_sounds import play_file as playsound

SYSOS = system().upper()

sfxpath = "bin/utils/sound/sfx_snake_"
sfx_ingame_path = sfxpath + "ingame.wav"
sfx_nav_path = sfxpath + "nav.wav"
sfx_eat_path = sfxpath + "yummy.wav"

action = "d"
w = curses.KEY_UP
a = curses.KEY_LEFT
s = curses.KEY_DOWN
d = curses.KEY_RIGHT


def game(speed: int, process: multiprocessing.Process) -> None:
    """Snake game main code."""
    global action, SYSOS
    screen = curses.initscr()
    screen.nodelay(1)
    screen.keypad(1)
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.can_change_color()

    dims = screen.getmaxyx()

    head = [1, 1]
    body = [head[:]] * 5

    screen.border()
    direction = 0
    dead = 0
    apple = 0
    remove = body[-1][:]
    yummy = "⬤"
    if SYSOS == "DARWIN":
        yummy = "●"

    while not dead:
        while not apple:
            y = secrets.randbelow(dims[0] - 2) + 1
            x = secrets.randbelow(dims[1] - 2) + 1
            if screen.inch(y, x) == ord(" "):
                apple = 1
                screen.addstr(y, x, yummy, curses.color_pair(1))
        if (remove in body) is False:
            screen.addch(
                remove[0],
                remove[1],
                " ",
            )
            curses.curs_set(0)
            screen.refresh()
        screen.addch(head[0], head[1], "■", curses.color_pair(2))
        action = screen.getch()
        if action == d and direction != 2:
            direction = 0
        elif action == s and direction != 3:
            direction = 1
        elif action == a and direction != 0:
            direction = 2
        elif action == w and direction != 1:
            direction = 3
        if direction == 0:
            head[1] += 1
        if direction == 1:
            head[0] += 1
        if direction == 2:
            head[1] -= 1
        if direction == 3:
            head[0] -= 1
        remove = body[-1][:]
        for i in range(len(body) - 1, 0, -1):
            body[i] = body[i - 1][:]
        body[0] = head[:]

        snake_yummy_stdout = (16788260, 9679, 11044)

        if screen.inch(head[0], head[1]) != ord(" "):
            # Snake munched the yummy!
            if screen.inch(head[0], head[1]) in snake_yummy_stdout:
                playsound(sfx_eat_path, 0)
                apple = 0
                body.append(body[-1])
            else:
                process.terminate()
                screen.clear()
                screen.refresh()
                dead = 1
        screen.refresh()
        time.sleep(speed)


def new_game_init(curses_ctx: Any, speed: int) -> None:
    """Menu to start a new game"""
    t1 = multiprocessing.Process(target=playsound, args=(sfx_ingame_path, 1))
    t1.start()
    curses.def_prog_mode()
    curses_ctx.clear()
    curses_ctx.refresh()
    game(speed, t1)
    curses_ctx.clear()
    curses.reset_prog_mode()  # reset to 'current' curses environment
    curses.curs_set(1)  # reset doesn't do this right
    curses.curs_set(0)


def main(curses_ctx: Any) -> None:
    """Wrapper function to run Snake externally"""
    # curses colours
    curses.init_pair(1, 1, 0)  # yummy
    curses.init_pair(2, 2, 0)  # snek

    while True:
        selection = open_menu(curses_ctx, items=("PLAY", "QUIT"), header="SNAKE")
        if selection == "QUIT":
            return  # to load back main menu
        if selection == "PLAY":
            selection = open_menu(
                curses_ctx, items=("EASY", "NORMAL", "SNEK GO BRRR"), header="SPEED"
            )
            if selection == "EASY":
                new_game_init(curses_ctx, speed=0.4)
            elif selection == "NORMAL":
                new_game_init(curses_ctx, speed=0.1)
            else:
                new_game_init(curses_ctx, speed=0.3 / 9)


if __name__ == "__main__":
    curses.wrapper(main)
    curses.endwin()
