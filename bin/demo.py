import curses
import os
from typing import Any

from initload import initialize
from play_sounds import play_file as playsound
from play_sounds import play_while_running
from utils.palettes import palettes

# Curses setup
screen = curses.initscr()
curses.noecho()
# curses.cbreak()
curses.start_color()
curses.can_change_color()
screen.keypad(1)

# Player metadata
METADATA = {
    "os": None,
    "py_version": False,
    "term_h_cur": None,
    "term_h_max": 32,
    "term_h_min": 32,
    "term_w_cur": None,
    "term_w_max": 106,
    "term_w_min": 80,
    "palette": palettes.Base16(),
}

# Run initload
METADATA = initialize(METADATA)
screen.clear()
# Import a colour palette as desired; see bin/utils/palettes/palettes.py
# METADATA["palette"] = palettes.Gruvbox()
# p = palettes.Gruvbox()


def colorinit(scr: object, metadata: dict) -> None:
    """Changes the colour theme of the screen."""
    curclrs = metadata["palette"].alias  # contains the list of colour name aliases

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
        RGB = metadata["palette"].to_rgb(curclrs[i], curses=True)
        curses.init_color(i, RGB[0], RGB[1], RGB[2])
        scr.refresh()


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
PYCOMMAND = "pycommand"
SETTING = "setting"
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
            "command": "bin/minesweep.py",
        },
        {
            "title": "BATTLESHIP",
            "type": COMMAND,
            "command": "bin/battleship/client.py",
        },
        {
            "title": "CONNECT FOUR",
            "type": COMMAND,
            "command": "bin/ConnectFour/blessedConnectFour.py",
        },
        {
            "title": "SNAKE",
            "type": COMMAND,
            "command": "bin/snake/snake.py",
        },
        # {
        #     "title": "CONTENT D - has submenus",
        #     "type": MENU,
        #     "subtitle": "Please select an option...",
        #     "options": [
        #         {
        #             "title": "Midnight Rescue",
        #             "type": COMMAND,
        #             "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SSR/SSR.EXE -exit",
        #         },
        #         {
        #             "title": "Outnumbered",
        #             "type": COMMAND,
        #             "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SSO/SSO.EXE -exit",
        #         },
        #         {
        #             "title": "Treasure Mountain",
        #             "type": COMMAND,
        #             "command": "dosbox /media/samba/Apps/dosbox/doswin/games/SST/SST.EXE -exit",
        #         },
        #     ],
        # },
        {"title": "CREDITS", "type": COMMAND, "command": "some command"},
        {
            "title": "change theme".upper(),
            "type": MENU,
            "subtitle": "select a theme".upper(),
            "options": [
                {"title": "base16".upper(), "type": SETTING, "command": "base16"},
                {"title": "commodore".upper(), "type": SETTING, "command": "commodore"},
                {"title": "dracula".upper(), "type": SETTING, "command": "dracula"},
                {"title": "gruvbox".upper(), "type": SETTING, "command": "gruvbox"},
                {"title": "haxx0r".upper(), "type": SETTING, "command": "hacker"},
                {"title": "jackal".upper(), "type": SETTING, "command": "jackal"},
                {"title": "nord".upper(), "type": SETTING, "command": "nord"},
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
                1,  # y
                2,  # x
                menu["title"],
                curses.color_pair(3),
            )
            # Subtitle
            screen.addstr(4, 4, menu["subtitle"], curses.color_pair(4))

            # Display all the menu items, showing the 'pos' item highlighted
            for index in range(optioncount):
                textstyle = idled
                if pos == index:
                    textstyle = selected
                screen.addstr(
                    5 + index,  # y
                    4,  # x
                    f'{index + 1} - {menu["options"][index]["title"]}',
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
            # convert keypress back to a number, then subtract 1 to get index
            pos = x - ord("0") - 1

        # down arrow
        elif x == 258:
            playsound("bin/utils/sound/sfx_menu_move4.wav", block=False)
            if pos < optioncount:
                pos += 1
            else:
                pos = 0

        # up arrow
        elif x == 259:
            playsound("bin/utils/sound/sfx_menu_move4.wav", block=False)
            if pos > 0:
                pos += -1
            else:
                pos = optioncount

    # return index of the selected item
    playsound("bin/utils/sound/sfx_menu_select4.wav", block=False)
    return pos


def processmenu(menu: dict, parent: Any = None) -> None:
    """Calls Showmenu and acts on the selected item"""
    global METADATA
    optioncount = len(menu["options"])
    exitmenu = False

    while not exitmenu:
        getin = displaymenu(menu, parent)

        if getin == optioncount:
            exitmenu = True

        # elif menu["options"][getin]["type"] == PYCOMMAND:
        #     if menu["options"][getin]["title"].lower == 'minesweeper':
        #         curses.reset_prog_mode()
        #         wipe(METADATA)
        #         curses.wrapper(minesweep.main)
        #         screen.clear()
        #         curses.curs_set(1)
        #         curses.curs_set(0)

        elif menu["options"][getin]["type"] == COMMAND:
            # save curent curses environment
            curses.def_prog_mode()
            wipe(METADATA)

            # clears previous screen
            screen.clear()

            # run the command
            pythonpath = "venv/bin/python"
            if METADATA['os'] != 'WINDOWS':
                os.system(f'{pythonpath} {menu["options"][getin]["command"]}')
            else:
                pythonpath = "py"  # py3.9?
                os.system(f'{pythonpath} {menu["options"][getin]["command"]}')

            # clear on keypress and update with new position
            screen.clear()
            curses.reset_prog_mode()  # reset to 'current' curses environment
            curses.curs_set(1)  # reset doesn't do this right
            curses.curs_set(0)

        elif menu["options"][getin]["type"] == SETTING:
            if menu["options"][getin]["command"].lower() == "base16":
                METADATA["palette"] = palettes.Base16()
                colorinit(screen, METADATA)
                screen.refresh()
            elif menu["options"][getin]["command"].lower() == "commodore":
                METADATA["palette"] = palettes.Commodore64()
                colorinit(screen, METADATA)
                screen.refresh()
                screen.refresh()
            elif menu["options"][getin]["command"].lower() == "dracula":
                METADATA["palette"] = palettes.Dracula()
                colorinit(screen, METADATA)
                screen.refresh()
            elif menu["options"][getin]["command"].lower() == "gruvbox":
                METADATA["palette"] = palettes.Gruvbox()
                colorinit(screen, METADATA)
                screen.refresh()
            elif menu["options"][getin]["command"].lower() == "hacker":
                METADATA["palette"] = palettes.Haxx0r()
                colorinit(screen, METADATA)
                screen.refresh()
            elif menu["options"][getin]["command"].lower() == "jackal":
                METADATA["palette"] = palettes.Jackal()
                colorinit(screen, METADATA)
                screen.refresh()
            elif menu["options"][getin]["command"].lower() == "nord":
                METADATA["palette"] = palettes.Nord()
                colorinit(screen, METADATA)
                screen.refresh()

        elif menu["options"][getin]["type"] == MENU:
            screen.clear()
            processmenu(menu["options"][getin], menu)
            screen.clear()
            curses.curs_set(1)  # reset doesn't do this right
            curses.curs_set(0)

        elif menu["options"][getin]["type"] == QUIT:
            exitmenu = True


# Main program
processmenu(menu_data)
curses.endwin()  # closes out the menu system and returns you to the bash prompt.
wipe(METADATA)
