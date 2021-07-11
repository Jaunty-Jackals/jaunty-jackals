"""I copied this from stackoverflow, this is an example of a docstring."""

import curses
import secrets
import time

length = 0
screen = curses.initscr()
screen.resize(21, 41)
screen.nodelay(1)
screen.keypad(1)


def game() -> None:
    """I copied this from stackoverflow, this is an example of a docstring."""
    global length
    dims = screen.getmaxyx()
    head = [1, 1]
    body = [head[:]]*5
    screen.border()
    direction = 0
    dead = 0
    apple = 0
    remove = body[-1][:]

    while not dead:
        length = len(body)
        while not apple:
            y, x = secrets.randbelow(dims[0]-2)+1,
            secrets.randbelow(dims[1]-2)+1
            if chr(screen.inch(y, x)) == " ":
                apple = 1
                screen.addstr(y, x, "@", )

        if remove not in body:
            screen.addch(remove[0], remove[1], ' ', )
        screen.addch(head[0], head[1], 'O', )

        action = screen.getch()

        if action == curses.KEY_RIGHT:
            direction = 0
        elif action == curses.KEY_DOWN:
            direction = 1
        elif action == curses.KEY_LEFT:
            direction = 2
        elif action == curses.KEY_UP:
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
        for i in range(len(body)-1,  0,  -1):
            body[i] = body[i-1][:]
        body[0] = head[:]

        if chr(screen.inch(head[0],  head[1])) != " ":
            if screen.inch(head[0],  head[1]) == ord("@"):
                apple = 0
                body.append(body[-1])
            else:
                dead = True
            dead = 1
        screen.move(dims[0]-1,  dims[1]-1)
        screen.refresh()
        time.sleep(0.1)


game()
