import logging
import time

import bs_game
from battleship.console import console
from play_sounds import play_while_running
from rich.prompt import IntPrompt, Prompt

logging.basicConfig(filename="log.log", level=logging.DEBUG)

SFX_INGAME_PATH = "bin/utils/sound/sfx_battleship_soundtrack.wav"


def main():
    """Game"""
    # Network setup
    host = "localhost"
    port = 5000
    last_shot_hit = False
    last_move = None
    player_won = False
    is_server = Prompt.ask("Are you a client or a server? (c/s)").lower()[0] == "s"
    player_turn = not is_server

    if not is_server:
        host = Prompt.ask(
            "Enter hostname (default: localhost)",
            default="localhost",
            show_default=False,
        )
        port = IntPrompt.ask(
            "Enter port (default: 5000)", default=5000, show_default=False
        )

    with bs_game.Network(host, port, is_server) as net, play_while_running(SFX_INGAME_PATH):
        # Initialise
        player_board = bs_game.create_empty_board()
        enemy_board = bs_game.create_empty_board()

        bs_game.place_ships(player_board, enemy_board)

        console.print("Okay, let's start:")
        bs_game.print_boards(player_board, enemy_board)

        # Game on
        while not bs_game.player_lost(player_board):

            if player_turn:
                x, y = bs_game.ask_player_for_shot()
                last_move = bs_game.Shot(x, y, last_shot_hit)
                net.send(bytes(last_move))

            else:
                console.print("Waiting for enemy's response...")
                data = net.recv()
                if not data:
                    player_won = True
                    break

                enemy_shot = bs_game.Shot.decode(data)

                # True if enemy hit player
                last_shot_hit = bs_game.update_player_board(enemy_shot, player_board)

                if last_move:
                    last_move.last_shot_hit = enemy_shot.last_shot_hit
                    bs_game.update_enemy_board(last_move, enemy_board)

            bs_game.print_boards(player_board, enemy_board)
            player_turn = not player_turn

        if player_won:
            console.print("You won!")
            time.sleep(3)
        else:
            console.print("You lost!")
            time.sleep(3)


if __name__ == "__main__":
    main()
