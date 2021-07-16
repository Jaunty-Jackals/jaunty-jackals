"""Snake."""

import curses
import secrets
import time

speed = 0.1

action = "d"

w = curses.KEY_UP
a = curses.KEY_LEFT
s = curses.KEY_DOWN
d = curses.KEY_RIGHT

screen = curses.initscr()
screen.resize(21, 41)
screen.nodelay(1)
screen.keypad(1)

curses.start_color()

curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)


def game() -> None:
    """Snake game main code."""
    global action
    dims = screen.getmaxyx()
    head = [1, 1]
    body = [head[:]] * 5
    screen.border()
    direction = 0
    dead = 0
    apple = 0
    remove = body[-1][:]

    while not dead:
        while not apple:
            y = secrets.randbelow(dims[0] - 2) + 1
            x = secrets.randbelow(dims[1] - 2) + 1
            if screen.inch(y, x) == ord(" "):
                apple = 1
                screen.addstr(y, x, "⬤", curses.color_pair(1))
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

        if screen.inch(head[0], head[1]) != ord(" "):
            if screen.inch(head[0], head[1]) == 16788260:
                apple = 0
                body.append(body[-1])
            else:
                dead = 1
        screen.move(dims[0] - 1, dims[1] - 1)
        screen.refresh()
        time.sleep(speed)

        
game()

curses.endwin()
