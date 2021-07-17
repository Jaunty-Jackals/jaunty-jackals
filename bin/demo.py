import curses
import os
from multiprocessing import Process
from typing import Any

from initload import initialize
from play_sounds import play_file as playsound
from utils.palettes import palettes

# Curses setup
screen = curses.initscr()
curses.noecho()
# curses.cbreak()
curses.start_color()
curses.can_change_color()
screen.keypad(1)
curses.curs_set(0)

# Player metadata
METADATA = {
    "os": None,
    "py_version": False,
    "term_h_cur": None,
    "term_h_max": 41,
    "term_h_min": 41,
    "term_w_cur": None,
    "term_w_max": 122,
    "term_w_min": 122,
    "palette": palettes.Jackal(),
}

# Import a colour palette as desired; see bin/utils/palettes/palettes.py
# METADATA["palette"] = palettes.Gruvbox()
# p = palettes.Gruvbox()


def colorinit(scr: Any, metadata: dict) -> None:
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
curses.init_pair(4, 5, 0)  # menu subtitle
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
            "command": "bin/bs_client.py",
        },
        {
            "title": "CONNECT FOUR",
            "type": COMMAND,
            "command": "bin/blessedConnectFour.py" if str(os.name).lower() != "nt" else "pass",
        },
        {
            "title": "SNAKE",
            "type": COMMAND,
            "command": "bin/snake.py",
        },
        {
            "title": "TETRIS",
            "type": COMMAND,
            "command": "bin/tetris.py",
        },
        {
            "title": "change theme".upper(),
            "type": MENU,
            "subtitle": "select a theme".upper(),
            "options": [
                {"title": "base16 3024 ".upper(), "type": SETTING, "command": "base16"},
                {
                    "title": "commodore 64".upper(),
                    "type": SETTING,
                    "command": "commodore",
                },
                {
                    "title": "dracula dark".upper(),
                    "type": SETTING,
                    "command": "dracula",
                },
                {"title": "grooby box".upper(), "type": SETTING, "command": "gruvbox"},
                {"title": "haxx0r green".upper(), "type": SETTING, "command": "hacker"},
                {
                    "title": "jackal original".upper(),
                    "type": SETTING,
                    "command": "jackal",
                },
                {
                    "title": "northern aurora".upper(),
                    "type": SETTING,
                    "command": "nord",
                },
            ],
        },
        {"title": "CREDITS", "type": COMMAND, "command": "bin/utils/macros/credits.py"},
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
                curses.COLS // 2 - len(menu["title"]) // 2,  # x
                menu["title"],
                curses.color_pair(3),
            )
            # Subtitle
            screen.addstr(
                4,
                curses.COLS // 2 - len(menu["subtitle"]) // 2,
                menu["subtitle"],
                curses.COLOR_MAGENTA,
            )

            # Display all the menu items, showing the 'pos' item highlighted
            for index in range(optioncount):
                textstyle = idled
                if pos == index:
                    textstyle = selected
                screen.addstr(
                    curses.LINES // 4 + 2 + index * 3,  # y
                    curses.COLS // 2 - len(menu["options"][index]["title"]) // 2,  # x
                    f'{menu["options"][index]["title"]}',
                    textstyle,
                )

            # Show Exit/Return at bottom of menu
            textstyle = idled
            if pos == optioncount:
                textstyle = selected
            screen.addstr(
                curses.LINES // 4 + 2 + optioncount * 3 + 1,
                curses.COLS // 2 - len(lastoption) // 2,
                f"{lastoption}",
                textstyle,
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

        elif menu["options"][getin]["type"] == COMMAND:
            # Save curent curses environment
            curses.def_prog_mode()
            wipe(METADATA)

            # Clears previous screen
            screen.clear()

            # run the command
            pythonpath = "python"
            if METADATA["os"] != "WINDOWS":
                # Reset terminal
                os.system("reset")

                # Inherit from selected base colour
                curclrs = METADATA["palette"].alias
                for i in range(len(curclrs)):
                    _RGB = METADATA["palette"].to_rgb(curclrs[i], curses=True)
                    curses.init_color(i, _RGB[0], _RGB[1], _RGB[2])
                    screen.refresh()

                # Execute
                os.system(f'{pythonpath} {menu["options"][getin]["command"]}')
            else:
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


if __name__ == "__main__":
    # Run initload
    METADATA = initialize(METADATA)
    wipe(METADATA)
    screen.clear()

    # Do menu things
    processmenu(menu_data)
    curses.endwin()
    wipe(METADATA)
