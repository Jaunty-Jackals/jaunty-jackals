import curses
import locale
import sys
from typing import TYPE_CHECKING, Any, Callable, Dict

from play_sounds import play_file as playsound
from play_sounds import play_while_running
from tetris.core import Game
from tetris.exceptions import CollisionError, OutOfBoundsError
from tetris.user_interface import (
    UserInterface,
    create_screens,
    make_color_pairs
)
from tetris.utils import Window

if TYPE_CHECKING:
    from tetris.core import Tetromino
else:
    Tetromino = Any


KeyBindings = Dict[int, Callable[[Tetromino], None]]

KEY_BINDINGS: KeyBindings = {
    curses.KEY_LEFT: lambda tetromino: tetromino.move_sideways("left"),
    curses.KEY_RIGHT: lambda tetromino: tetromino.move_sideways("right"),
    curses.KEY_DOWN: lambda tetromino: tetromino.move_down(),
    ord("s"): lambda tetromino: tetromino.move_all_the_way_down(),
    ord("a"): lambda tetromino: tetromino.rotate("left"),
    ord("d"): lambda tetromino: tetromino.rotate("right"),
}


def main(stdscr: Window) -> None:
    """Main function called from outside with all attributes"""
    locale.setlocale(locale.LC_ALL, "")
    stdscr.nodelay(True)
    curses.curs_set(False)

    border_screen, inner_screen = create_screens(stdscr)

    assert border_screen is not None, "minimum screen size required"
    assert inner_screen is not None, "minimum screen size required"

    make_color_pairs()

    inner_screen.timeout(100)
    inner_screen.keypad(True)

    user_interface = UserInterface(stdscr, inner_screen)
    game = Game(inner_screen, user_interface)

    while True:
        for screen in (inner_screen, border_screen, stdscr):
            screen.erase()

        border_screen.box(0, 0)

        user_interface.render_landed_tetrominos(game.grid)
        user_interface.render_current_tetromino(game.tetromino)
        user_interface.render_next_tetromino(game.next_tetromino)
        user_interface.render_instructions()
        user_interface.render_score(game.score)

        stdscr.refresh()
        inner_screen.refresh()

        if not game.paused:
            game.handle_falling()
            game.clear_rows()

        try:
            user_input = inner_screen.getch()
        except curses.error:
            continue
        except KeyboardInterrupt:
            sys.exit()

        if user_input == ord("p"):
            game.pause()

        elif user_input == ord("q"):
            return

        elif not game.paused and user_input in KEY_BINDINGS:
            try:
                KEY_BINDINGS[user_input](game.tetromino)
            except (CollisionError, OutOfBoundsError):
                continue
