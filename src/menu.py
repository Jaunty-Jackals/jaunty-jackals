from asciimatics.effects import Cog, Print, Cycle
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import sys
import os


def demo(screen):
    # basic configs
    figfont = 'puffy'

    # message
    if screen.width != 80 or screen.height not in (24, 25):
        if os.name.upper() == 'NT':  # windows
            effects = [
                Print(screen,
                      FigletText("Resize to", font=figfont),
                      y=screen.height // 2 - 8
                      ),

                Cycle(screen,
                      FigletText('8 0  x  2 5', font=figfont),
                      y=screen.height // 2
                      )
            ]
        else:  # other
            effects = [
                Print(screen,
                      FigletText("Resize to", font=figfont),
                      y=screen.height // 2 - 8),

                Cycle(screen,
                      FigletText('8 0  x  2 4', font=figfont),
                      y=screen.height // 2)
            ]
    else:
        # do main stuff
        effects = [
            Cog(screen, 20, 10, 10),
            Cog(screen, 60, 30, 15, direction=-1),
            Print(screen, FigletText("ascii", font="smkeyboard"),
                  attr=Screen.A_BOLD, x=47, y=3, start_frame=50),
            Print(screen, FigletText("matics", font="smkeyboard"),
                  attr=Screen.A_BOLD, x=45, y=7, start_frame=100),
            Print(screen, FigletText("by Peter Brittain", font="term"),
                  x=8, y=22, start_frame=150)
        ]
    screen.play([Scene(effects, -1)], stop_on_resize=True)


while True:
    try:
        Screen.wrapper(demo)
        sys.exit(0)
    except ResizeScreenError:
        pass
