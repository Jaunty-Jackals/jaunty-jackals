import curses
import os
from typing import Any

from bin.utils.palettes import palettes

screen = curses.initscr()
METADATA = {'os': os.name, 'term_h_cur': None, 'term_h_max': (screen.getmaxyx())[0], 'term_h_min': None,
            'term_w_cur': None, 'term_w_max': (screen.getmaxyx())[1], 'term_w_min': None}

curses.noecho()
curses.cbreak()
curses.start_color()
curses.can_change_color()
screen.keypad(1)
p = palettes.Base16_3024()
curclrs = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

for i in range(len(curclrs)):
    RGB = p.to_rgb(curclrs[i], curses=True)
    curses.init_color(i, RGB[0], RGB[1], RGB[2])

# Change this to use different colors when highlighting
curses.init_pair(1, curses.COLOR_BLACK,
                 curses.COLOR_RED)  # Sets up color pair #1, it does black text with white background
h = curses.color_pair(1)  # h is the coloring for a highlighted menu option
n = curses.A_NORMAL  # n is the coloring for a non highlighted menu option

MENU = "menu"
COMMAND = "command"
EXITMENU = "exitmenu"

menu_data = {
    'title': "JackalOS GAME CONSOLE", 'type': MENU, 'subtitle': "SELECT",
    'options': [
        {'title': "MINE SWEEPER", 'type': COMMAND, 'command': 'venv/bin/python3.9 minesweep/minesweep.py'},
        {'title': "CONTENT B", 'type': COMMAND, 'command': 'emulationstation'},
        {'title': "CONTENT C", 'type': COMMAND, 'command': 'uqm'},
        {'title': "CONTENT D - has submenus", 'type': MENU, 'subtitle': "Please select an option...",
         'options': [
             {'title': "Midnight Rescue", 'type': COMMAND,
              'command': 'dosbox /media/samba/Apps/dosbox/doswin/games/SSR/SSR.EXE -exit'},
             {'title': "Outnumbered", 'type': COMMAND,
              'command': 'dosbox /media/samba/Apps/dosbox/doswin/games/SSO/SSO.EXE -exit'},
             {'title': "Treasure Mountain", 'type': COMMAND,
              'command': 'dosbox /media/samba/Apps/dosbox/doswin/games/SST/SST.EXE -exit'},
         ]
         },
        {'title': "CREDITS", 'type': COMMAND,
         'command': 'some command'},
        {'title': "SETTINGS - has submenus", 'type': MENU, 'subtitle': "Select Yes to Reboot",
         'options': [
             {'title': "NO", 'type': EXITMENU, },
             {'title': "", 'type': COMMAND, 'command': ''},
             {'title': "", 'type': COMMAND, 'command': ''},
             {'title': "", 'type': COMMAND, 'command': ''},
             {'title': "YES", 'type': COMMAND, 'command': 'sudo shutdown -r -time now'},
             {'title': "", 'type': COMMAND, 'command': ''},
             {'title': "", 'type': COMMAND, 'command': ''},
             {'title': "", 'type': COMMAND, 'command': ''},
         ]
         },

    ]
}


def runmenu(menu: dict, parent: Any) -> Any:
    """Displays the appropriate menu and returns the option selected"""
    # work out what text to display as the last menu option
    if parent is None:
        lastoption = "Exit"
    else:
        lastoption = "Return to %s menu" % parent['title']

    optioncount = len(menu['options'])  # how many options in this menu

    pos = 0
    oldpos = None
    x = None

    # Loop until return key is pressed
    while x != ord('\n'):
        if pos != oldpos:
            oldpos = pos
            screen.border(0)
            screen.addstr(2, 2, menu['title'], curses.A_STANDOUT)  # Title for this menu
            screen.addstr(4, 2, menu['subtitle'], curses.A_BOLD)  # Subtitle for this menu

            # Display all the menu items, showing the 'pos' item highlighted
            for index in range(optioncount):
                textstyle = n
                if pos == index:
                    textstyle = h
                screen.addstr(5 + index, 4, "%d - %s" % (index + 1, menu['options'][index]['title']), textstyle)
            # Now display Exit/Return at bottom of menu
            textstyle = n
            if pos == optioncount:
                textstyle = h
            screen.addstr(5 + optioncount, 4, "%d - %s" % (optioncount + 1, lastoption), textstyle)
            screen.refresh()
            # finished updating screen

        x = screen.getch()  # Gets user input

        # What is user input?
        if ord('1') <= x <= ord(str(optioncount + 1)):
            pos = x - ord('0') - 1  # convert keypress back to a number, then subtract 1 to get index
        elif x == 258:  # down arrow
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == 259:  # up arrow
            if pos > 0:
                pos += -1
            else:
                pos = optioncount

    # return index of the selected item
    return pos


def processmenu(menu: Any, parent: Any = None) -> Any:
    """Calls Showmenu and acts on the selected item"""
    optioncount = len(menu['options'])
    exitmenu = False
    while not exitmenu:  # Loop until the user exits the menu
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] == COMMAND:
            curses.def_prog_mode()  # save curent curses environment
            os.system('reset')
            if menu['options'][getin]['title'] == 'Pianobar':
                os.system('amixer cset numid=3 1')  # Sets audio output on the pi to 3.5mm headphone jack
            screen.clear()  # clears previous screen
            os.system(menu['options'][getin]['command'])  # run the command
            screen.clear()  # clears previous screen on key press and updates display based on pos
            curses.reset_prog_mode()  # reset to 'current' curses environment
            curses.curs_set(1)  # reset doesn't do this right
            curses.curs_set(0)
            os.system('amixer cset numid=3 2')  # Sets audio output on the pi back to HDMI
        elif menu['options'][getin]['type'] == MENU:
            screen.clear()  # clears previous screen on key press and updates display based on pos
            processmenu(menu['options'][getin], menu)  # display the submenu
            screen.clear()  # clears previous screen on key press and updates display based on pos
        elif menu['options'][getin]['type'] == EXITMENU:
            exitmenu = True


# Main program
processmenu(menu_data)
curses.endwin()  # closes out the menu system and returns you to the bash prompt.
os.system('clear')
