import curses
import time
from typing import Any

jackal_ascii_medium = [
    "...`                                `--`",
    "``.+o.                           `:/-`` ",
    "`` `+dy.`                      .oyo` `` ",
    " .  `-dm/.`                 `-oNm:` `.  ",
    " ``  `/mN/```           ````-sMh:`  `   ",
    " ```  .oh//```..`````````  -omh:` ```   ",
    "   ``  `/.:                .:s.```.`    ",
    "   `.`` ``                     ````     ",
    "    ```   `.` ```  `  ``````.`  `.      ",
    "    `.    `.::-+-` .  `-/.++``   ``     ",
    "     .    `..-:/.`     ----..`   ``     ",
    "     ``   ``    ..     .`  `..  `.      ",
    "     `..` ````  `       ```````..`````  ",
    "   ````..``````.``/sso````````.` ``  `` ",
    " ``   .. ```.-..` .sh:  `.`.` ` `..   ``",
    "..     . -----:--+/sd/o/---:..-. `    `.",
    " .       .        `````````````.      ``",
    " ````````                       ``````` ",
]


def jackal_logo(screen: Any) -> None:
    """Jaunty Jackals logo"""
    pass


def status(screen: Any, msg: str, passed: Any, pos: list, sleep: float = 0.25) -> None:
    """Sends out a status message during initialisation"""
    curses.init_pair(5, 2, 0)  # PASS
    curses.init_pair(6, 1, 0)  # FAIL
    curses.init_pair(7, 3, 0)  # CHECK
    curses.init_pair(8, 5, 0)  # WARN
    curses.init_pair(17, 6, 0)  # normal item

    logtext = curses.color_pair(17)
    passtext = curses.color_pair(5)
    failtext = curses.color_pair(6)
    checktext = curses.color_pair(7)
    warntext = curses.color_pair(8)

    passorfail = None
    if passed is True:
        passorfail = "PASS"
        passorfail_color = passtext
    elif passed is False:
        passorfail = "FAIL"
        passorfail_color = failtext
    elif passed is None:
        passorfail = "CHCK"
        passorfail_color = checktext
    elif passed == "WARN":
        passorfail = "WARN"
        passorfail_color = warntext

    screen.addstr(pos[0] + 1, pos[1], "[", logtext)
    screen.addstr(pos[0] + 1, pos[1] + 2, f"{passorfail}", passorfail_color)
    screen.addstr(pos[0] + 1, pos[1] + 7, "]", logtext)
    screen.addstr(pos[0] + 1, pos[1] + 9, f"{msg}", logtext)
    screen.refresh()
    time.sleep(sleep)
