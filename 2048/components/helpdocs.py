#!/usr/bin/env python3

"""
Help module for the 2048 game

Provides classes with help documents.
"""

_help_text = """\
This is the help document for the 2048 game.

The goal is to get the piece with the value of 2048 (or greater). This is done by joining pieces with the same value. Two pieces are merged into the one with twice the value.

Merging is done when two pieces meet while moving.  Movement of pieces is done in one of the four directions with the cursor keys.

Game ends when there are no available moves (no free tiles, and no available merges).

Press '?' to close this help, 'r' to restart the game, and <ESC> to exit.
"""

def get_help_text():
    return _help_text
