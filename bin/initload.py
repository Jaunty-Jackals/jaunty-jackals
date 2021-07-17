import curses
import time
from os import environ as _env
from platform import python_version, system

from play_sounds import play_file as playsound
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
    screen.keypad(True)
    screen.border(0)

    # Happy sound
    initsound = "bin/utils/sound/sfx_init.wav"
    warnsound = "bin/utils/sound/sfx_init_warn.wav"
    playsound(initsound, block=True)

    while not complete:

        p = palettes.Jackal()
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

        # Position counter
        acpi_pos_y = 0
        acpi_pos_x = 1
        curses.def_prog_mode()

        # System environment settings
        _envk = list(_env.keys())
        # _envv = list(_env.values())

        # Check OS
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
                f"{os_ver.upper()} detected".upper(),
                passed=True,
                pos=[acpi_pos_y, acpi_pos_x],
            )
            acpi_pos_y += 1
            metadata["os"] = os_ver.upper()

            # Show some _env values
            windows_terminal = []

            for key in _envk:
                if "WT_" in key:
                    windows_terminal.append(key)

            if len(windows_terminal) != 0:
                playsound(warnsound, block=True)
                status(
                    screen,
                    "windows terminal detected".upper(),
                    passed="Warn",
                    pos=[acpi_pos_y, acpi_pos_x],
                    sleep=1.0,
                )
                acpi_pos_y += 1
                playsound(warnsound, block=True)
                status(
                    screen,
                    "users may not be able to change color themes".upper(),
                    passed="Warn",
                    pos=[acpi_pos_y, acpi_pos_x],
                    sleep=2.0,
                )
                acpi_pos_y += 1

            # Ensure position y is not overflowing
            # for i in range(10 - acpi_pos_y):
            #     status(
            #         screen,
            #         f'{_envk[i]}',
            #         passed=None,
            #         pos=[acpi_pos_y, acpi_pos_x],
            #         sleep=0.1,
            #     )
            #     acpi_pos_y += 1
            #     status(
            #         screen,
            #         f'{_envv[i]}',
            #         passed=True,
            #         pos=[acpi_pos_y, acpi_pos_x],
            #         sleep=0.1,
            #     )
            #     acpi_pos_y += 1

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
                if int(py_ver[2]) == 9 and int(py_ver[4]) in (2, 5, 6):
                    status(
                        screen,
                        f"Python {py_ver} DETECTED    ".upper(),
                        passed=True,
                        pos=[acpi_pos_y, acpi_pos_x],
                    )
                    acpi_pos_y += 1
                    metadata["py_version"] = True
                else:
                    status(
                        screen,
                        f"Python {py_ver} DETECTED    ".upper(),
                        passed=True,
                        pos=[acpi_pos_y, acpi_pos_x],
                    )
                    acpi_pos_y += 1
                    playsound(warnsound, block=True)
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
                playsound(warnsound, block=True)
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

        # Check if virtualenv
        is_venv = False
        for key in _envk:
            if "VIRTUAL_ENV" in key:
                is_venv = True

        if is_venv:
            status(
                screen,
                "virtual environment detected".upper(),
                passed=True,
                pos=[acpi_pos_y, acpi_pos_x],
            )
            acpi_pos_y += 1
        elif is_venv is False:
            status(
                screen,
                "no virtual environment detected".upper(),
                passed="Warn",
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=1.0,
            )
            acpi_pos_y += 1
            status(
                screen,
                "you must be in a virtual environment!".upper(),
                passed=False,
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=5.0,
            )
            break

        # Detect screensize
        status(screen, "screen size".upper(), passed=None, pos=[acpi_pos_y, acpi_pos_x])
        screen.refresh()
        acpi_pos_y += 1

        screen_y = (screen.getmaxyx())[0]
        metadata["term_h_cur"] = screen_y
        screen_x = (screen.getmaxyx())[1]
        metadata["term_w_cur"] = screen_x
        status(
            screen,
            f"{screen_x} by {screen_y} detected     ".upper(),
            passed=True,
            pos=[acpi_pos_y, acpi_pos_x],
            sleep=0.5,
        )
        screen.refresh()
        acpi_pos_y += 1

        # Width is too small
        if screen_x < metadata["term_w_min"]:
            playsound(warnsound, block=True)
            status(
                screen,
                f'screen width of {screen_x} is smaller than the recommended {metadata["term_w_min"]}'.upper(),
                passed=False,
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=2.0,
            )
            screen.refresh()
            acpi_pos_y += 1
            break

        # Width is too long
        elif screen_x > metadata["term_w_max"]:
            playsound(warnsound, block=True)
            status(
                screen,
                f'screen width of {screen_x} is bigger than the recommended {metadata["term_w_max"]}'.upper(),
                passed="warn",
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=0.5,
            )
            screen.refresh()
            acpi_pos_y += 1

        # Height is too small
        if screen_y < metadata["term_h_min"]:
            playsound(warnsound, block=True)
            status(
                screen,
                f'screen height of {screen_y} is smaller than the recommended {metadata["term_h_min"]}'.upper(),
                passed=False,
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=2.0
            )
            screen.refresh()
            acpi_pos_y += 1
            break

        # Height is too long
        elif screen_y > metadata["term_h_max"]:
            playsound(warnsound, block=True)
            status(
                screen,
                f'screen height of {screen_y} is bigger than the recommended {metadata["term_h_max"]}'.upper(),
                passed="warn",
                pos=[acpi_pos_y, acpi_pos_x],
                sleep=1.0,
            )
            screen.refresh()
        time.sleep(1.0)
        complete = True

    return metadata
