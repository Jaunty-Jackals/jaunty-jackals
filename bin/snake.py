"""Snake."""

import curses
import secrets
import time

from platform import system
from typing import Any

from minesweep.minesweep_utils import open_menu
from play_sounds import play_file as playsound
from play_sounds import play_while_running

from multiprocessing.dummy import Pool as ThreadPool

pool = ThreadPool(4)

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

screen = curses.initscr()
# screen.resize(21, 41)
screen.nodelay(1)
screen.keypad(1)

curses.start_color()


def game(speed: int) -> None:
    """Snake game main code."""
    global action, SYSOS
    dims = (21, 41)
    head = [1, 1]
    body = [head[:]] * 5
    screen.border()
    direction = 0
    dead = 0
    apple = 0
    remove = body[-1][:]
    yummy = "⬤"
    if SYSOS == 'DARWIN':
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

        if screen.inch(head[0], head[1]) != ord(" "):
            # Snake munched the yummy!
            if screen.inch(head[0], head[1]) in (16788260, 9679):
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


def new_game_init(curses_ctx: Any, speed: int) -> None:
    """Menu to start a new game"""
    # with play_while_running(sfx_ingame_path, block=True): #problem cause
    screen.clear()
    screen.refresh()
    game(speed)


def main(curses_ctx: Any) -> None:
    """Wrapper function to run Snake externally"""
    # curses colours
    curses.init_pair(1, 1, 0)  # yummy
    curses.init_pair(2, 2, 0)  # snek

    while True:
        selection = open_menu(
            curses_ctx, items=("PLAY", "QUIT"), header="SNAKE"
        )
        if selection == "QUIT":
            return  # to load back main menu
        if selection == "PLAY":
            selection = open_menu(
            curses_ctx, items=("1 - BAD PLAYER","0.1 - NORMAL", "0.01 - SNEK"), header="SPEED"
            )
            if selection == "1 - BAD PLAYER":
                new_game_init(curses_ctx, speed=1)
            elif selection == "0.1 - NORMAL":
                new_game_init(curses_ctx, speed=0.1)
            else:
                new_game_init(curses_ctx, speed=0.01)

                
if __name__ == "__main__":
    curses.wrapper(main)
    curses.endwin()
