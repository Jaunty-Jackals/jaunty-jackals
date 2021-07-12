#!/usr/bin/env python3

from . import gamectrl

import curses
import enum

class _CursesInputStates(enum.Enum):
    """
    Possible states of the input component
    """
    cis_init = 1
    cis_normal = 2
    cis_help_window = 3

class CursesInput:
    """
    Cuses input class

    Contains everything necessary to translate the input events from the 
    given curses window to the commands for the output, and the game
    logic components.
    """

    _MOVEMENT_KEYS_TRANSL = {
            curses.KEY_UP: gamectrl.MovementDirections.up,
            curses.KEY_DOWN: gamectrl.MovementDirections.down,
            curses.KEY_LEFT: gamectrl.MovementDirections.left,
            curses.KEY_RIGHT: gamectrl.MovementDirections.right
            }

    def __init__(self, window, game_ctrl, output):
        """
        Initialization method

        Inputs are: keystrokes input curses window, game controller, and
        the output.
        """

        self._window = window

        self._game_ctrl = game_ctrl
        self._output = output

        # needs to register to the game controller
        self._game_ctrl.attach_input(self)

        self._state = _CursesInputStates.cis_init

    def get_input(self):
        """
        Reads, and interprets a keyboard input

        One keystroke can produce at most one action. Also,
        interpretation is state-dependant.
        """

        pressed_key = self._window.getch()

        # always checked keypresses
        #

        if pressed_key == curses.KEY_RESIZE:
            self._output.update_size()
            return
        elif pressed_key == 0x1b:
            self._game_ctrl.close_game()
            return
        elif pressed_key == ord('?'):
            if self._state == _CursesInputStates.cis_help_window:
                # state change
                self._output.close_help()
                self._state = self._old_state
            else:
                self._output.open_help()
                # state change
                self._old_state = self._state
                self._state = _CursesInputStates.cis_help_window
            return

        # state-dependent checks
        #

        if self._state == _CursesInputStates.cis_init:
            self._output.close_intro_window()
            self._game_ctrl.resume_game()
            # state change
            self._state = _CursesInputStates.cis_normal
            return
        elif self._state == _CursesInputStates.cis_normal:
            if pressed_key == ord('r'):
                self._game_ctrl.reset_game()
                return
            elif pressed_key in CursesInput._MOVEMENT_KEYS_TRANSL:
                self._game_ctrl.move_pieces(
                        CursesInput._MOVEMENT_KEYS_TRANSL[pressed_key])
                return
        elif self._state == _CursesInputStates.cis_help_window:
            if pressed_key == curses.KEY_RIGHT:
                self._output.current_win_next_page()
                return
            elif pressed_key == curses.KEY_LEFT:
                self._output.current_win_previous_page()
                return

    def is_operational(self):
        """
        Get the operational state of the component

        Returns the information if this component is able to function
        properly.
        """

        return True
