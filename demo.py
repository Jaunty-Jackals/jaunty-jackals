import curses
import os
from typing import Any

from utils.palettes import palettes

screen = curses.initscr()
METADATA = {
    "os": os.name,
    "term_h_cur": None,
    "term_h_max": (screen.getmaxyx())[0],
    "term_h_min": None,
    "term_w_cur": None,
    "term_w_max": (screen.getmaxyx())[1],
    "term_w_min": None,
}

curses.noecho()
curses.cbreak()
curses.start_color()
curses.can_change_color()
screen.keypad(1)

# Import a colour palette as desired
p = palettes.Commodore64()  # see bin/utils/palettes/palettes.py
curclrs = p.alias  # contains the list of colour name aliases

for i in range(len(curclrs)):
    """COLOUR ORDER AND ALIASES

    Follows typical ANSI colour formatting + foreground and background (which equal to one of the 16)

    Normal
    0       1       2       3       4       5       6       7
    black   red     green   yellow  blue    magenta cyan    white

    Brighter (add "bright" prefix)
    8       9       10      11      12      13      14      15
    black   red     green   yellow  blue    magenta cyan    white

    Other
    16      17
    fg      bg
    """
    RGB = p.to_rgb(curclrs[i], curses=True)
    curses.init_color(i, RGB[0], RGB[1], RGB[2])

# colour pairs for highlights
curses.init_pair(1, 14, 0)  # selected text
curses.init_pair(2, 1, 0)  # idle text
selected = curses.color_pair(1)
idled = curses.color_pair(2)

MENU = "menu"
OSCOMMAND = "command"
PYCOMMAND = "command"
EXITMENU = "exitmenu"

menu_data = {
    "title": "JackalOS GAME CONSOLE",
    "type": MENU,
    "subtitle": "",
    "options": [
        {
            "title": "MINE SWEEPER",
            "type": OSCOMMAND,
            "command": "venv/bin/python3.9 minesweep/minesweep.py",
        },
        {
            "title": "BATTLESHIP",
            "type": OSCOMMAND,
            "command": "venv/bin/python3.9 battleship/client.py",
        },
        {
            "title": "CONNECT FOUR",
            "type": OSCOMMAND,
            "command": "venv/bin/python3.9 ConnectFour/blessedConnectFour.py",
        },
        {"title": "CONTENT C", "type": PYCOMMAND, "command": "uqm"},
        {
            "title": "CONTENT D - has submenus",
            "type": MENU,
            "subtitle": "Please select an option...",
            "options": [
                {
                    "title": "Midnight Rescue",
                    "type": OSCOMMAND,
                    "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SSR/SSR.EXE -exit",
                },
                {
                    "title": "Outnumbered",
                    "type": PYCOMMAND,
                    "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SSO/SSO.EXE -exit",
                },
                {
                    "title": "Treasure Mountain",
                    "type": PYCOMMAND,
                    "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SST/SST.EXE -exit",
                },
            ],
        },
        {"title": "CREDITS", "type": PYCOMMAND, "command": "some command"},
        {
            "title": "SETTINGSs",
            "type": MENU,
            "subtitle": "Select Yes to Reboot",
            "options": [
                {
                    "title": "NO",
                    "type": EXITMENU,
                },
                {"title": "", "type": PYCOMMAND, "command": ""},
                {"title": "", "type": PYCOMMAND, "command": ""},
                {"title": "", "type": PYCOMMAND, "command": ""},
                {
                    "title": "YES",
                    "type": PYCOMMAND,
                    "command": "sudo shutdown -r -time now",
                },
                {"title": "", "type": PYCOMMAND, "command": ""},
                {"title": "", "type": PYCOMMAND, "command": ""},
                {"title": "", "type": PYCOMMAND, "command": ""},
            ],
        },
    ],
}


def runmenu(menu: dict, parent: Any) -> Any:
    """Displays the appropriate menu and returns the option selected"""
    # work out what text to display as the last menu option
    if parent is None:
        lastoption = "EXIT"
    else:
        lastoption = "Return to %s menu" % parent["title"]

    optioncount = len(menu["options"])  # games in the menu

    pos = 0
    oldpos = None
    x = None

    # Loop until return key is pressed
    while x != ord("\n"):
        if pos != oldpos:
            oldpos = pos
            screen.bkgd(17)
            screen.border(17)
            screen.addstr(2, 2, menu["title"], curses.A_STANDOUT)  # Title for this menu
            screen.addstr(
                4,
                2,
                menu["subtitle"],
            )  # Subtitle for this menu

            # Display all the menu items, showing the 'pos' item highlighted
            for index in range(optioncount):
                textstyle = idled
                if pos == index:
                    textstyle = selected
                screen.addstr(
                    5 + index,  # y
                    4,  # x
                    "%d - %s" % (index + 1, menu["options"][index]["title"]),
                    textstyle,
                )
            # Now display Exit/Return at bottom of menu
            textstyle = idled
            if pos == optioncount:
                textstyle = selected
            screen.addstr(
                5 + optioncount, 4, "%d - %s" % (optioncount + 1, lastoption), textstyle
            )
            screen.refresh()
            # finished updating screen

        x = screen.getch()

        # Get input
        if ord("1") <= x <= ord(str(optioncount + 1)):
            pos = (
                x - ord("0") - 1
            )  # convert keypress back to a number, then subtract 1 to get index
        elif x == 258:  # KEY_DOWN
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == 259:  # KEY_UP
            if pos > 0:
                pos += -1
            else:
                pos = optioncount

    # return index of the selected item
    return pos


def processmenu(menu: Any, parent: Any = None) -> Any:
    """Calls Showmenu and acts on the selected item"""
    optioncount = len(menu["options"])
    exitmenu = False
    while not exitmenu:  # Loop until the user exits the menu
        getin = runmenu(menu, parent)
        if getin == optioncount:
            exitmenu = True

        # OS-based command
        elif menu["options"][getin]["type"] == OSCOMMAND:
            curses.def_prog_mode()  # save curent curses environment
            os.system("reset")
            screen.clear()  # clears previous screen
            os.system(menu["options"][getin]["command"])  # run the command
            screen.clear()  # clears previous screen on key press and updates display based on pos
            curses.reset_prog_mode()  # reset to 'current' curses environment
            curses.curs_set(1)  # reset doesn't do this right
            curses.curs_set(0)

        # Python-based command
        elif menu["options"][getin]["type"] == PYCOMMAND:
            screen.clear()
            screen.clear()

        # process submenu
        elif menu["options"][getin]["type"] == MENU:
            screen.clear()
            processmenu(menu["options"][getin], menu)  # display the submenu
            screen.clear()

        # exit
        elif menu["options"][getin]["type"] == EXITMENU:
            exitmenu = True


# Main program
processmenu(menu_data)
curses.endwin()

# OS-specific clear
if METADATA["os"].upper() == "POSIX":
    os.system("clear")
elif METADATA["os"].upper() == "NT":
    os.system("CLS")
