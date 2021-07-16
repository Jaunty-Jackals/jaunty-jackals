import curses
import random
import sys
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

import more_itertools
from tetris.exceptions import CollisionError, GameOverError, OutOfBoundsError
from tetris.utils import Window

if TYPE_CHECKING:
    from tetris.user_interface import UserInterface  # pylint: disable=cyclic-import
else:
    UserInterface = Any


SHAPES: Dict[str, List[int]] = {
    "O": [51],
    "I": [8738, 240],
    "S": [54, 561],
    "Z": [99, 306],
    "J": [275, 71, 802, 113],
    "L": [547, 116, 785, 23],
    "T": [114, 305, 39, 562],
}

COLORS: Dict[str, int] = {
    "I": curses.COLOR_YELLOW,
    "O": curses.COLOR_BLUE,
    "T": curses.COLOR_GREEN,
    "L": curses.COLOR_RED,
    "J": curses.COLOR_MAGENTA,
    "S": curses.COLOR_CYAN,
    "Z": curses.COLOR_WHITE,
}

DIRECTIONS: Dict[str, int] = {"right": 1, "left": -1}

GRID_WIDTH: int = 20
GRID_HEIGHT: int = 30

Grid = List[List[List[Optional[int]]]]
ShapeVec = List[Sequence[int]]


class Game:
    """Class to manage the different game state"""

    def __init__(self, screen: Window, user_interface: UserInterface):
        self.screen = screen
        self.user_interface = user_interface
        self.grid = [[[0, None] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.tetromino: Tetromino = Tetromino(self.grid)
        self.next_tetromino: Tetromino = Tetromino(self.grid)
        self.counter: int = 0
        self.score: int = 0
        self.paused: bool = False

    def clear_rows(self) -> None:
        """Clears all the filled rows and prepends the grid with an empty row."""
        for row in self.grid.copy():
            if all(x[0] == 1 for x in row):
                self.grid.remove(row)
                self.grid.insert(0, [[0, None] for _ in range(GRID_WIDTH)])
                self.score += GRID_WIDTH

    def handle_falling(self) -> None:
        """Function to manage the dominos falling

        Handles automatic tetromino falling (every 0.5 seconds), as well as
        landing in case the tetromino touches the ground or another tetromino.

        Besides that, it displays game over screen in case the GameOverError is raised.

        Score is updated appropriately, too.
        """
        self.counter += 1
        if self.counter == 5:
            try:
                self.tetromino.move_down()
            except (CollisionError, OutOfBoundsError):
                try:
                    self.tetromino.land()
                except GameOverError:
                    sys.exit()
                else:
                    self.tetromino = self.next_tetromino
                    self.next_tetromino = Tetromino(self.grid)
            finally:
                self.counter = 0

    def restart(self) -> None:
        """Restarts the game by putting all vital game parameters to initial state."""
        self.grid = [[[0, None] for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.tetromino = Tetromino(self.grid)
        self.next_tetromino = Tetromino(self.grid)
        self.counter = 0
        self.score = 0

    def pause(self) -> None:
        """Pauses or resumes the gameplay."""
        self.paused = not self.paused


class Tetromino:
    """Class that forms the individual blocks"""

    def __init__(self, grid: Grid):
        self.grid = grid
        self.letter = random.choice(list(SHAPES.keys()))
        self.shape = random.choice(SHAPES[self.letter])
        self.topleft = [0, GRID_WIDTH // 2 - 1]
        self.color = curses.color_pair(COLORS[self.letter])

    def land(self) -> None:
        """Lands a tetromino. If top left corner of the tetromino is beyond upper boundary, raises GameOverError."""
        if self.topleft[0] <= 0:
            raise GameOverError

        for rowidx, row in enumerate(to_4x4(self.shape)):
            for colidx, block in enumerate(row):
                if block != 0:
                    y, x = self.topleft
                    self.grid[rowidx + y][colidx + x][0] = block
                    self.grid[rowidx + y][colidx + x][1] = self.color

    def move_sideways(self, direction: str) -> None:
        """Main move side function

        Moves a tetromino one step left or right if another tetromino is not in its way,
        whilst making sure it does not go out of bounds at the same time.
        """
        for rowidx, row in enumerate(to_4x4(self.shape)):
            for colidx, block in enumerate(row):
                if block != 0:
                    y, x = self.topleft
                    if colidx + x + DIRECTIONS[direction] not in range(GRID_WIDTH):
                        raise OutOfBoundsError
                    if self.grid[rowidx + y][colidx + x + DIRECTIONS[direction]][0] != 0:
                        raise CollisionError

        self.topleft[1] += DIRECTIONS[direction]

    def move_down(self) -> None:
        """Main move down function

        Moves a tetromino one step down if another tetromino is not in its way,
        whilst making sure it does not go out of bounds at the same time.
        """
        for rowidx, row in enumerate(to_4x4(self.shape)):
            for colidx, block in enumerate(row):
                if block != 0:
                    y, x = self.topleft
                    if rowidx + y + 1 >= GRID_HEIGHT:
                        raise OutOfBoundsError
                    elif self.grid[rowidx + y + 1][colidx + x][0] != 0:
                        raise CollisionError

        self.topleft[0] += 1

    def move_all_the_way_down(self) -> None:
        """Main function to move all way down

        Moves a tetromino all the way down until it either goes out of bounds,
        or until another tetromino is encountered.
        """
        while True:
            try:
                self.move_down()
            except (OutOfBoundsError, CollisionError):
                break

    def rotate(self, direction: str) -> None:
        """Main function to rotate tetromino

        Rotates a tetromino either left or right if another tetromino is not in its way,
        whilst making sure it does not go out of bounds.
        """
        current_rotation = SHAPES[self.letter].index(self.shape)
        next_rotation = current_rotation + DIRECTIONS[direction]

        potential_shape = SHAPES[self.letter][next_rotation % len(SHAPES[self.letter])]

        for rowidx, row in enumerate(to_4x4(potential_shape)):
            for colidx, block in enumerate(row):
                if block != 0:
                    y, x = self.topleft
                    if colidx + x not in range(GRID_WIDTH):
                        raise OutOfBoundsError
                    if rowidx + y >= GRID_HEIGHT:
                        raise OutOfBoundsError
                    if self.grid[rowidx + y][colidx + x][0] != 0:
                        raise CollisionError

        self.shape = potential_shape


def to_4x4(rotation: int) -> ShapeVec:
    """Converts any tetromino into list of 2d vector"""
    tmp = [(rotation >> 15 - i) & 1 for i in range(16)]
    return list(more_itertools.sliced(tmp, 4))
