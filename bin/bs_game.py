import logging
import os
import socket
import struct
from dataclasses import dataclass
from itertools import chain, repeat
from typing import Any, List, Tuple

from battleship.console import console
from play_sounds import play_file as playsound
from play_sounds import play_while_running
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

PERMITTED_LETTERS = "abcdefghij0123456789-"
FIELDS = [
    EMPTY,
    OWN_SHIP,
    OWN_SHIP_HIT,
    ENEMY_SHIP_HIT,
    MISS,
    OWN_SHIP_ENEMY_SHIP_HIT,
] = (0, 1, 2, 3, 4, 5)
SHIP_TYPES = [BATTLESHIP, CRUISER, DESTROYER, SUBMARINE] = (
    5,
    4,
    3,
    2,
)  # Supported ship types.
SHIP_NAMES = {
    BATTLESHIP: "Battleship",
    CRUISER: "Cruiser",
    DESTROYER: "Destroyer",
    SUBMARINE: "Submarine",
}
PLAYER_SHIPS = [BATTLESHIP, SUBMARINE]  # Change this according to your needs.

PATH = "bin/utils/sound/sfx_battleship_"
sfx_explosion_path = PATH + "explosion.wav"
sfx_splash_path = PATH + "water_splash.wav"


layout = Layout(name="root")
layout.split_column(
    Layout(name="adjust", size=1),
    Layout(name="legend", size=3),
    Layout(name="header", size=3),
    Layout(name="main"),
    Layout(name="footer", size=3, visible=False),
)
layout["header"].split_row(Layout(name="header_left"), Layout(name="header_right"))
layout["main"].split_row(Layout(name="left"), Layout(name="right"))

# Insert blank line at the top to compensate for input line at the bottom
layout["adjust"].update(Text(" "))

# Key
text = Text(
    "Own Ship: \u2588 | Own Ship Hit: X | Enemy Ship Hit: \u2588 | Enemy Ship Miss: \u2588",
    justify="center",
)
text.stylize("green on green", 10, 11)
text.stylize("red on green", 28, 29)
text.stylize("red on red", 48, 49)
text.stylize("yellow on yellow", 69, 70)
layout["legend"].update(Panel(text, title="KEY"))


class Error(ValueError):
    """Monkey patch ValueError to log the exceptions to a log file."""

    def __init__(self, *args):
        logging.error(str(self))
        super().__init__(*args)


def print_err(*args, **kwargs):
    """Print an error in red."""
    console.print(*args, **kwargs, style="red")


@dataclass
class Shot:
    """
    Dataclass to store and decode/encode shot information for communication between two clients.

    +-------+-------+-------+---------+
    |   X   |   Y   |  Hit  | Padding |
    +-------+-------+-------+---------+
    | 4 Bit | 4 Bit | 1 Bit | 7 Bit   |
    +-------+-------+-------+---------+
    """

    x: int
    y: int
    last_shot_hit: bool = False

    def __bytes__(self):
        """Encode the shot as packed binary data."""
        if self.x >= 2 ** 4:
            raise Error(
                f"X={self.x} is too large to fit into 4 bit: {hex(self.x)} > 0xf."
            )
        if self.y >= 2 ** 4:
            raise Error(
                f"X={self.y} is too large to fit into 4 bit: {hex(self.y)} > 0xf."
            )

        return struct.pack("!BB", (self.x << 4) | self.y, int(self.last_shot_hit) << 7)

    @staticmethod
    def decode(pkt: Any) -> Any:
        """Decode a packet into a Shot instance."""
        xy, h = struct.unpack("!BB", pkt)
        return Shot(xy >> 4, xy & 0xF, h >> 7)


def coord_valid(coord: int) -> bool:
    """Return True if a given x or y coordinates is in bounds."""
    return 0 <= coord <= 9


Board = List[List[int]]


def create_table_board(board: Board, person: str) -> Table:
    """Create Rich Table object of Board."""
    vertical_header = [" ", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", " "]

    if person == "you":
        table = Table(*vertical_header, title="Your Board", show_lines=True)
    elif person == "enemy":
        table = Table(*vertical_header, title="Enemy Board", show_lines=True)

    for row_no, row in enumerate(board):
        lst = []
        lst.append(str(row_no))
        for col in row:
            if col == EMPTY:
                lst.append(Text(" ", style="white on black"))
            elif col == OWN_SHIP:
                lst.append(Text("\u2588", style="green on green"))
            elif col == OWN_SHIP_HIT:
                lst.append(Text("X", style="red on green"))
            elif col == ENEMY_SHIP_HIT:
                lst.append(Text("\u2588", style="red on red"))
            elif col == MISS:
                lst.append(Text("\u2588", style="yellow on yellow"))
        lst.append(str(row_no))
        table.add_row(*lst)

    return table


def print_boards(board: Board, enemy_board: Board) -> None:
    """
    Prints the full board including padding, color and spaces directly to stdout.

    Note: Due to use of ANSI Color codes it might not work on windows.
    """
    your_table = create_table_board(board, "you")
    enemy_table = create_table_board(enemy_board, "enemy")

    layout["left"].update(Panel(your_table, expand=False))
    layout["right"].update(Panel(enemy_table, expand=False))

    layout["header_left"].update(
        Panel(
            Text(
                f"Your Score: {list(chain.from_iterable(enemy_board)).count(ENEMY_SHIP_HIT)}/{sum(PLAYER_SHIPS)}",
                justify="center",
            )
        )
    )
    layout["header_right"].update(
        Panel(
            Text(
                f"Enemy Score: {list(chain.from_iterable(board)).count(OWN_SHIP_HIT)}/{sum(PLAYER_SHIPS)}",
                justify="center",
            )
        )
    )

    # Clear the screen on Windows
    if os.name == "nt":
        _ = os.system("cls")
    # Clear the screen on OSX and Linux
    else:
        _ = os.system("clear")

    console.print(layout)
    return


def create_empty_board():
    """Return a 10x10 array of zeros."""
    return [10 * [0] for _ in repeat(0, 10)]


def update_player_board(shot: Shot, board: Board):
    """
    Update the player board for a given shot by the enemy. Marks Hits on own ship.

    :param shot: the shot to evaluate
    :param board: the board to update (by ref)
    :return: True if the last shot hit an ship of us else False
    """
    x = shot.x
    y = shot.y
    field = board[y][x]

    if field == OWN_SHIP:
        board[y][x] = OWN_SHIP_HIT
        return True
    return False


def update_enemy_board(shot: Shot, board: Board):
    """
    Update the enemy board after a shot has been fired. Marks Misses and Hits.

    :param shot: the shot to evaluate
    :param board: the board to update (by ref)
    :return: None
    """
    x = shot.x
    y = shot.y
    field = board[y][x]

    if shot.last_shot_hit or field == ENEMY_SHIP_HIT:
        playsound(sfx_explosion_path, block=False)
        board[y][x] = ENEMY_SHIP_HIT
    else:
        playsound(sfx_splash_path, block=False)
        board[y][x] = MISS


def player_lost(board: Board):
    """Return True if the current player has no ships left."""
    return not any(OWN_SHIP in set(x) for x in board)


class Network:
    """
    Network communication protocol using TCP sockets.

    Replace this class for a custom implementation.

    Supports classic instantiation or the use as a context manager.
    """

    BUFSIZE = 16

    def __init__(self, host: str, port: int, is_server: bool) -> None:
        """
        Functionality is almost the same for client and server. It differs slightly.

        :param host: the host to either connect to (as client) or to open the server in (as server)
        :param port: the port to connect to (as client) or to open as server
        :param is_server: True if the returned instance should act as a TCP server.
        """
        self.is_server = is_server
        self.sock = None
        self.conn = None

        if self.is_server:
            # Create a new socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((host, port))
            self.sock.listen()
            logging.debug("Server is listening on port " + str(port))

        else:
            # Connect to a remote host
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))

    def _server_send(self, pkt: Any) -> Any:
        self.conn.sendall(pkt)

    def _client_send(self, pkt: Any) -> Any:
        self.sock.send(pkt)

    def send(self, pkt: Any):
        """
        Send arbitrary to remote

        :param pkt: packet as binary data
        """
        if self.is_server:
            return self._server_send(pkt)
        return self._client_send(pkt)

    def _server_recv(self) -> int:
        """Receive in server."""
        if self.conn is None:
            while True:
                logging.debug("Server is waiting for a connection.")
                self.conn, self.addr = self.sock.accept()
                break

        logging.debug("Waiting for Data")

        while True:
            data = self.conn.recv(self.BUFSIZE)
            if not data:
                break
            return data

    def _client_recv(self) -> int:
        """Receive in client."""
        data = self.sock.recv(self.BUFSIZE)
        return data

    def recv(self) -> Any:
        """
        Wait for a packet to arrive.

        Note: BLOCKING!
        """
        try:
            if self.is_server:
                return self._server_recv()
            return self._client_recv()
        except Exception:
            self.close()

    def close(self):
        """
        Close the socket and free all resources.

        Make sure this method is always called (also in case of failure to prevent stuck resources or ports)
        """
        self.sock.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Enter"""
        # Enables context manager.
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        """Exit"""
        # Enables context manager.
        self.close()


def parse_shot(shot_string: str):
    """Check if shot is valid."""
    shot_string = shot_string.lower().replace(" ", "")
    shot_string = "".join([c if c in PERMITTED_LETTERS else "" for c in shot_string])

    if len(shot_string) < 2:
        raise Error("Invalid String provided!")

    # Convert input into numbers between 0 and 9.
    try:
        x = ord(shot_string[0]) - 97
        y = int(shot_string[1])
    except ValueError:
        raise Error("Invalid String provided!")

    if not coord_valid(x):
        raise Error("X out of bounds!")

    if not coord_valid(y):
        raise Error("Y out of bounds!")

    return x, y


def ask_player_for_shot():
    """Ask until the player gives a valid input."""
    while True:
        try:
            return parse_shot(Prompt.ask("Shoot (Format XY, e.g. A4)"))
        except Error as err:
            print_err(err)


def ask_player_for_ship(ship_type: int):
    """Ask until the player gives a valid input and has placed all of the ships."""
    length = ship_type
    while True:
        ship_input = Prompt.ask(
            f"Place your {SHIP_NAMES.get(ship_type)} (length: {length}) formatted as XY - XY (e.g. A1-A5)"
        )
        # Assume the following format: XX - YY and ask until the user enters something valid.
        try:
            a, b = ship_input.lower().replace(" ", "").split("-")
            a0, a1 = parse_shot(a)
            b0, b1 = parse_shot(b)

            # Validate ship.
            # Ships can be either vertical or horizontal. So only one dimension can change: a-z or 1-9
            if a0 != b0 and a1 != b1:
                print_err("Ships cannot be diagonal.")
                continue

            # Out of bounds
            if any([not coord_valid(x) for x in [a0, a1, b0, b1]]):
                print_err("Ships coordinates out of bounds.")
                continue

            # Length
            if max(abs(a0 - b0), abs(a1 - b1)) != (length - 1):
                print_err(f"Ship must be exactly {length} fields long.")
                continue

            return (a0, a1), (b0, b1)

        except (IndexError, ValueError) as e:
            print_err("Invalid Format:", str(e))


def place_ship(a: Tuple[int, int], b: Tuple[int, int], board: Board) -> None:
    """
    Update the board and place a ship on it.

    :param a: Start X, Y coords
    :param b: End X, Y coords
    :param board: board to update
    """
    a0, a1 = a
    b0, b1 = b

    if a0 != b0 and a1 != b1:
        raise Error("Ship cannot be diagonal!")

    if a0 == b0 and a1 == b1:
        raise Error("Ship must have more than one square!")

    # Iterate over the squares until a0 == b0 and b1 == b1.
    while True:
        if board[a1][a0] != EMPTY:
            raise Error("Field already occupied!")

        board[a1][a0] = OWN_SHIP

        if a0 != b0:
            a0 += 1 * (-1 if a0 > b0 else 1)

        elif a1 != b1:
            a1 += 1 * (-1 if a1 > b1 else 1)

        if a0 == b0 and a1 == b1:
            board[a1][a0] = OWN_SHIP
            return


def place_ships(board: Board, enemy_board: Board) -> None:
    """Place all ships and ask the user for each position."""
    for ship in PLAYER_SHIPS:
        print_boards(board, enemy_board)
        while True:
            try:
                coords = ask_player_for_ship(ship)
                place_ship(*coords, board)
                break
            except ValueError as err:
                print_err(str(err))
