"""Snake."""

import curses
import secrets
import time

# from multiprocessing.dummy import Pool as ThreadPool
from platform import system
from typing import Any

from minesweep.minesweep_utils import open_menu
from play_sounds import play_file as playsound
from play_sounds import play_while_running

# pool = ThreadPool(4)

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


def game(speed: float) -> None:
    """Snake game main code."""
    global action, SYSOS

    screen = curses.initscr()
    screen.nodelay(1)
    screen.keypad(1)
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.can_change_color()
    screen.keypad(True)
    screen.border(0)

    dims = (
        (screen.getmaxyx())[0],
        (screen.getmaxyx())[1],
    )  # ensure map size = terminal size
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
        screen.refresh()

        snake_yummy_stdout = (16788260, 9679, 11044)

        if screen.inch(head[0], head[1]) != ord(" "):
            # Snake munched the yummy!
            if screen.inch(head[0], head[1]) in snake_yummy_stdout:
                playsound(sfx_eat_path, block=False)
                apple = 0
                body.append(body[-1])
            else:
                screen.clear()
                screen.refresh()
                dead = 1
        screen.move(dims[0] - 1, dims[1] - 1)
        screen.refresh()
        time.sleep(speed)


def new_game_init(curses_ctx: Any, speed: float) -> None:
    """Menu to start a new game"""
    # with play_while_running(sfx_ingame_path, block=True): #problem cause
    curses.def_prog_mode()
    curses_ctx.clear()
    curses_ctx.refresh()
    game(speed)
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
        selection = open_menu(curses_ctx, items=("PLAY", "EXIT"), header=" SNAKE ")
        if selection == "EXIT":
            return  # to load back main menu
        if selection == "PLAY":
            selection = open_menu(
                curses_ctx,
                items=("EASY", "NORMAL", "SNEK GO BRRR"),
                header=" DIFFICULTY ",
            )
            if selection == "EASY":
                new_game_init(curses_ctx, speed=0.4)
            elif selection == "NORMAL":
                new_game_init(curses_ctx, speed=0.1)
            else:
                new_game_init(curses_ctx, speed=0.033)


if __name__ == "__main__":
    curses.wrapper(main)
    curses.endwin()
