#!/usr/bin/python3.9

import curses
from typing import Any


class Rect:
    """Basic class to store rect attributes"""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def minmax(val: Any, minval: Any, maxval: Any) -> Any:
    """Return bound for the value within min and max"""
    return max(min(val, maxval), minval)


def draw_rect(curse_context: Any, rect: Any, header: str = "") -> Any:
    """Function to  return lines for any rect"""
    template = [
        ["\u250C", "\u2500", "\u2510"],
        ["\u2502", " ", "\u2502"],
        ["\u2514", "\u2500", "\u2518"],
    ]

    for h in range(rect.height):
        fillheader = 0
        fill = ""
        if h == 0:
            k = 0
            fillheader = len(header)
            fill = header
        elif h < rect.height - 1:
            k = 1
        else:
            k = 2
        gapfill_left = int(max((rect.width - 2 - fillheader), 0) / 2)
        gapfill_rgt = rect.width - 2 - fillheader - gapfill_left
        line = (
            template[k][0]
            + gapfill_left * template[k][1]
            + fill
            + gapfill_rgt * template[k][1]
            + template[k][2]
        )
        curse_context.addstr(rect.y + h, rect.x, line)
    return Rect(rect.x + 1, rect.y + 1, rect.width - 2, rect.height - 2)


def open_menu(curse_context: Any, items: tuple, header: str = "") -> Any:
    """General function to display any menu and return selected"""
    width = len(items) + 20
    height = len(items * 2) - 1 + 4
    curses.curs_set(False)
    sel = 0

    while True:
        center = (curses.COLS // 2, curses.LINES // 2)
        rect = Rect(center[0] - width // 3, center[1] - height // 2, width, height)
        rect = draw_rect(curse_context, rect, header.upper())

        for i, item in enumerate(items):
            attr = curses.A_NORMAL
            if i == sel:
                attr = curses.A_STANDOUT
            curse_context.addstr(
                rect.y + 1 + i * 2,
                center[0] - len(item) // 2 + 4,
                item.upper(),
                attr
            )

        c = curse_context.getch()
        if c == curses.KEY_UP:
            sel -= 1
        if c == curses.KEY_DOWN:
            sel += 1
        if c == curses.KEY_ENTER or c == 10:
            break
        sel = minmax(sel, 0, len(items) - 1)

    curses.curs_set(True)
    return items[sel]


def open_menu_no_rect(curse_context: Any, items: tuple) -> Any:
    """General function to display menu without rectangular border"""
    # width = len(items) + 20
    # height = len(items * 2) - 1 + 4
    curses.curs_set(False)
    sel = 0

    while True:
        # center = (curses.COLS // 2, curses.LINES // 2)
        # rect = Rect(center[0] - width // 2, center[1] - height // 2, width, height)
        # rect = draw_rect(curse_context, rect, header)

        for i, item in enumerate(items):
            attr = curses.A_NORMAL
            if i == sel:
                attr = curses.A_STANDOUT
            curse_context.addstr(
                curses.COLS // 2 - i * 2,
                curses.LINES // 2,
                item,
                attr
            )

        c = curse_context.getch()
        if c == curses.KEY_UP:
            sel -= 1
        if c == curses.KEY_DOWN:
            sel += 1
        if c == curses.KEY_ENTER or c == 10:
            break
        sel = minmax(sel, 0, len(items) - 1)

    curses.curs_set(True)
    return items[sel]
