import curses
import os
from typing import Any

from playsound import playsound

from initload import initialize
from utils.palettes import palettes

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
curses.can_change_color()
screen.keypad(1)

METADATA = {
    "os": None,
    "py_version": False,
    "term_h_cur": None,
    "term_h_max": None,
    "term_h_min": None,
    "term_w_cur": None,
    "term_w_max": None,
    "term_w_min": None,
    "palette": palettes.Commodore64(),
}

# run initload
METADATA = initialize(METADATA)
screen.clear()
playsound("utils/assets/sound/passing_time_in_wav.wav", block=False)

# Import a colour palette as desired; see bin/utils/palettes/palettes.py
METADATA["palette"] = palettes.Gruvbox()
# p = palettes.Gruvbox()
curclrs = METADATA["palette"].alias  # contains the list of colour name aliases

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
    RGB = METADATA["palette"].to_rgb(curclrs[i], curses=True)
    curses.init_color(i, RGB[0], RGB[1], RGB[2])

# Change this to use different colors when highlighting
curses.init_pair(3, 3, 0)  # menu title
curses.init_pair(4, 6, 0)  # menu subtitle
curses.init_pair(16, 10, 0)  # menu highlighted item
curses.init_pair(17, 7, 0)  # menu normal item

color_title = curses.color_pair(3)
color_subtitle = curses.color_pair(4)
selected = curses.color_pair(16)
idled = curses.color_pair(17)

MENU = "menu"
COMMAND = "command"
QUIT = "exitmenu"
LOAD = "load"

menu_data = {
    "title": "JackalOS GAME CONSOLE",
    "type": MENU,
    "subtitle": "SELECT",
    "options": [
        {
            "title": "MINE SWEEPER",
            "type": COMMAND,
            "command": "venv/bin/python3.9 minesweep/minesweep.py",
        },
        {
            "title": "BATTLESHIP",
            "type": COMMAND,
            "command": "venv/bin/python3.9 battleship/client.py",
        },
        {
            "title": "CONNECT FOUR",
            "type": COMMAND,
            "command": "venv/bin/python3.9 ConnectFour/blessedConnectFour.py",
        },
        {
            "title": "SNAKE",
            "type": COMMAND,
            "command": "venv/bin/python3.9 snake/snake.py",
        },
        {"title": "CONTENT C", "type": COMMAND, "command": "uqm"},
        {
            "title": "CONTENT D - has submenus",
            "type": MENU,
            "subtitle": "Please select an option...",
            "options": [
                {
                    "title": "Midnight Rescue",
                    "type": COMMAND,
                    "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SSR/SSR.EXE -exit",
                },
                {
                    "title": "Outnumbered",
                    "type": COMMAND,
                    "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SSO/SSO.EXE -exit",
                },
                {
                    "title": "Treasure Mountain",
                    "type": COMMAND,
                    "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SST/SST.EXE -exit",
                },
            ],
        },
        {"title": "CREDITS", "type": COMMAND, "command": "some command"},
        {
            "title": "SETTINGS - has submenus",
            "type": MENU,
            "subtitle": "Select Yes to Reboot",
            "options": [
                {
                    "title": "NO",
                    "type": QUIT,
                },
                {"title": "", "type": COMMAND, "command": ""},
                {"title": "", "type": COMMAND, "command": ""},
                {"title": "", "type": COMMAND, "command": ""},
                {
                    "title": "YES",
                    "type": COMMAND,
                    "command": "sudo shutdown -r -time now",
                },
                {"title": "", "type": COMMAND, "command": ""},
                {"title": "", "type": COMMAND, "command": ""},
                {"title": "", "type": COMMAND, "command": ""},
            ],
        },
    ],
}


def wipe(metadata: dict) -> None:
    """Clears the terminal by sending the os-specific clear command"""
    if metadata["os"] in "WINDOWS":
        os.system("CLS")
    else:
        os.system("clear")


def displaymenu(menu: dict, parent: Any) -> Any:
    """Displays the appropriate menu and returns the option selected"""
    # work out what text to display as the last menu option
    if parent is None:
        lastoption = "QUIT CONSOLE"
    else:
        lastoption = "RETURN"

    optioncount = len(menu["options"])  # how many options in this menu

    pos = 0
    oldpos = None
    x = None

    # Loop until return key is pressed
    while x != ord("\n"):
        if pos != oldpos:
            oldpos = pos
            screen.border(0)
            # screen.box(2, 2)
            # Title
            screen.addstr(
                curses.LINES // 2,  # y
                curses.COLS // 2 - len(menu["title"]) // 2,  # x
                menu["title"],
                curses.color_pair(3),
            )
            # Subtitle
            # screen.addstr(curses.LINES - 1,curses.COLS - 1,menu["subtitle"],curses.color_pair(4))

            # Display all the menu items, showing the 'pos' item highlighted
            for index in range(optioncount):
                textstyle = idled
                if pos == index:
                    textstyle = selected
                screen.addstr(
                    5 + index,
                    4,
                    "%d - %s"
                    % (index + 1, menu["options"][index]["title"]),  # TODO: fstring
                    textstyle,
                )

            # Now display Exit/Return at bottom of menu
            textstyle = idled
            if pos == optioncount:
                textstyle = selected
            screen.addstr(
                5 + optioncount,
                4,
                "%d - %s" % (optioncount + 1, lastoption),
                textstyle,  # TODO: fstring
            )

            # update screen
            screen.refresh()

        # Gets user input
        x = screen.getch()

        # What is user input?
        if ord("1") <= x <= ord(str(optioncount + 1)):
            pos = (
                x - ord("0") - 1
            )  # convert keypress back to a number, then subtract 1 to get index
        elif x == 258:  # down arrow
            playsound("utils/assets/sound/sfx_menu_move4.wav", block=False)
            if pos < optioncount:
                pos += 1
            else:
                pos = 0
        elif x == 259:  # up arrow
            playsound("utils/assets/sound/sfx_menu_move4.wav", block=False)
            if pos > 0:
                pos += -1
            else:
                pos = optioncount

    # return index of the selected item
    playsound("utils/assets/sound/sfx_menu_select4.wav", block=False)
    return pos


def processmenu(menu: dict, parent: Any = None) -> None:
    """Calls Showmenu and acts on the selected item"""
    optioncount = len(menu["options"])
    exitmenu = False

    while not exitmenu:
        getin = displaymenu(menu, parent)

        if getin == optioncount:
            exitmenu = True

        elif menu["options"][getin]["type"] == COMMAND:
            # save curent curses environment
            curses.def_prog_mode()
            wipe(METADATA)

            # clears previous screen
            screen.clear()

            # run the command
            os.system(menu["options"][getin]["command"])

            # clear on keypress and update with new position
            screen.clear()
            curses.reset_prog_mode()  # reset to 'current' curses environment
            curses.curs_set(1)  # reset doesn't do this right
            curses.curs_set(0)

        elif menu["options"][getin]["type"] == MENU:
            screen.clear()
            processmenu(menu["options"][getin], menu)
            screen.clear()

        elif menu["options"][getin]["type"] == QUIT:
            exitmenu = True


def get_metadata() -> dict:
    """Returns user's sysinfo variable METADATA as dictionary"""
    global METADATA
    return METADATA


# Main program
processmenu(menu_data)
curses.endwin()  # closes out the menu system and returns you to the bash prompt.
wipe(METADATA)
