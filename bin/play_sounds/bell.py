from contextlib import contextmanager
from typing import ContextManager

BELL_CHAR = "\a"
NO_NEWLINE = ""


def bell():
    """Play a ding sound"""
    print(BELL_CHAR, end=NO_NEWLINE)


@contextmanager
def bell_after(play_bell: bool = True) -> ContextManager:
    """Play a ding after a task if finished"""
    try:
        yield

    finally:
        if play_bell:
            bell()
