import curses
from platform import python_version, system

from utils.macros.handy import status
from utils.palettes import palettes


def initialize(metadata: dict) -> dict:
    """Initial loading screen from

    Used for establishing the player's system info
    """
    complete = False

    # Set up curses screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.can_change_color()
    # screen.resize(24, 80)
    screen.keypad(True)
    screen.border(0)

    while not complete:

        p = palettes.Base16()
        curclrs = p.alias

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
            rgb = p.to_rgb(curclrs[i], curses=True)
            curses.init_color(i, rgb[0], rgb[1], rgb[2])

        # Initial colours
        curses.init_pair(3, 3, 0)  # menu title
        curses.init_pair(4, 6, 0)  # menu subtitle
        curses.init_pair(5, 2, 0)  # PASS
        curses.init_pair(6, 1, 0)  # FAIL
        curses.init_pair(16, 9, 0)  # menu highlighted item
        curses.init_pair(17, 4, 0)  # menu normal item

        acpi_pos_y = 0  # position counter
        acpi_pos_x = 1
        curses.def_prog_mode()

        # Check OS [ FAIL ]
        status(
            screen,
            "operating system".upper(),
            passed=None,
            pos=[acpi_pos_y, acpi_pos_x],
            sleep=1.0,
        )
        acpi_pos_y += 1
        os_ver = system()
        if os_ver.upper() in ("WINDOWS", "DARWIN", "LINUX"):
            status(
                screen,
                f"{os_ver.upper()} DETECTED",
                passed=True,
                pos=[acpi_pos_y, acpi_pos_x],
            )
            acpi_pos_y += 1
            metadata["os"] = os_ver.upper()
        else:
            status(
                screen,
                "UNSUPPORTED OS DETECTED",
                passed=False,
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=5,
            )
            break

        # Check Python version
        status(screen, "PYTHON VERSION", passed=None, pos=[acpi_pos_y, acpi_pos_x])
        acpi_pos_y += 1

        py_ver = python_version()
        if int(py_ver[0]) == 3:
            if int(py_ver[2]) in (9, 10):
                if int(py_ver[2]) == 9 and int(py_ver[4]) in (4, 5, 6):
                    status(
                        screen,
                        f"Python {py_ver} DETECTED    ",
                        passed=True,
                        pos=[acpi_pos_y, acpi_pos_x],
                    )
                    acpi_pos_y += 1
                    metadata["py_version"] = True
                else:
                    status(
                        screen,
                        f"Python {py_ver} DETECTED    ",
                        passed=True,
                        pos=[acpi_pos_y, acpi_pos_x],
                    )
                    acpi_pos_y += 1
                    status(
                        screen,
                        "You are either using an older version of Python 3.9".upper(),
                        passed="WARN",
                        pos=[acpi_pos_y, acpi_pos_x],
                    )
                    acpi_pos_y += 1
                    status(
                        screen,
                        "OR using a version newer than 3.10.0".upper(),
                        passed="WARN",
                        pos=[acpi_pos_y, acpi_pos_x],
                    )
                    acpi_pos_y += 1
                    status(
                        screen,
                        "You may encounter unforeseen issues not tested by the developers".upper(),
                        passed="WARN",
                        pos=[acpi_pos_y, acpi_pos_x],
                        sleep=4.0,
                    )
                    acpi_pos_y += 1
                    metadata["py_version"] = True
            else:
                status(
                    screen,
                    "You must use Python 3.9+! Aborting...",
                    passed=False,
                    pos=[acpi_pos_y, acpi_pos_x],
                    sleep=4.0,
                )
                break
        else:
            status(
                screen,
                "Invalid Version of Python! Aborting...",
                passed=False,
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=4.0,
            )
            break

        # Detect screensize
        status(screen, "screen size".upper(), passed=None, pos=[acpi_pos_y, acpi_pos_x])
        screen.refresh()
        acpi_pos_y += 1

        screen_y = (screen.getmaxyx())[0]
        screen_x = (screen.getmaxyx())[1]
        status(
            screen,
            f"{screen_x} by {screen_y} detected     ".upper(),
            passed=True,
            pos=[acpi_pos_y, acpi_pos_x],
            sleep=5.0,
        )
        screen.refresh()
        acpi_pos_y += 1

        complete = True

    return metadata
