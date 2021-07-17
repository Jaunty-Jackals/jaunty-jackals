import curses
import time

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
curses.curs_set(0)
curses.can_change_color()
screen.keypad(True)
screen.border(0)

mypad = curses.newpad(120, 120)
mypad_pos = 0
credit_text = (
    """\

















                                    ╒╖_                                  ▄π
                                     ÑÑ▌v_                            ▄φ▓▒▌
                                     ▌▒▒▌_▀▄                       ▄∞│▄▒▒▐
                                     ╫î▒▒█⌐ █W▄                 _█▀ *█▒▒LΓ
                                      ▌Ü▒▒▀⌐ ▀╙W            ,_m▒█▄ ▄█▒▒▒▀
                                      ╙▄Ü▒▓▌└█▀░╙M█▀▒▒╙└└╙╙▀▄░░▀╝ ▄▒▒▒▒▀
                                       ╙▌▒▒▒█▄Z░░░░░░░░░░░░░░░░▀▀¢▒▒▒▒▀
                                        ▀▀▒▒└░░░░░░░░░░░░░░░░░░░░│▒┴▒╞
                                         └▒░░░▄ª  ⁿªj░░¿░░╒`└▄__ª¿░░Γ▌
                                          ▌░░░▒µ███▒▀░░╚░░j▀██▌█▒░░░▒▌
                                          ╞▒░░▐`└"╩└┌▒░░░░░▌╙^└ ╘W░░yL
                                          ╒▌▒░░½...▒M▒▒▒▒▒░▒...⌂▒│░▄▀
                                         _█▄▌▒▒TY>≈┌"▒▒▄▄▄▒ ╘▒▒▄⌂"█▀╩▒▒▒½▄
                                      ▄Φ└░▄╜``j═#M▄ - ████─ .▄▄z≈    "┤░░└W
                                      Ö░░░└L.╕ `²╙▒Ay▄▄╣▀▄▄▄∞╙ _.«╖▄J▌░░░░j┘
                                     ╪░░░░░┘░█└     ` ⁿ╜╝╜``  ` ``_▌░░░░░░j─
                                     ╘▄░░░░▄¥                      └╜▒▄▄▄4╜







                        .        µ             ╓φφ             µ         gφφφµ     g         ╥▄W
                @▄███▓██▄      @██╬     ▓█     ▓█▓   @▄       ▓▄ ║████████▓▀╜╙  "╙▓▄▄     @▓█╩
                 `"""
    """▓     @█▀▀█┐    ▓█     `▓█╬  ▓█▓,    ,▓█ `""` ▓█▓         `╙▀▀▓Ñ▄▄██▓
                        ▓▓   ▓▀▓  ▀█.   ▓╣      ▐█▓  ▓█▀▀▓╖  ▓██      ▐▓,               ▓██╜
                        ▓▓  ▓███▓▓╩▀▓   ▓█       ▐▓  ▓█`  ▓▓ ▓█▓      g█╣              ╥▓▓
                ╙▓▄φφφg▓█  ▓        ▓█  ▓██     ▄▓   ▓█   ╙▓████      ▓█╝             ▓█Ñ
                  ╙╙▓█▓╜  ╙▓         ▓▓  ╙▓█▄@▄▓╩    ╙▓      ╙╜╙      ▓▓            »@Ñ╜

                   ,╓g g       ╓φ            ╓╖gφ,   ╓g    ,╖╜▓       g       ▄▄φ          ╥µφφ
                @▓██████▄     @███      ,@╬╬╝╜╙ ╙╙    ▓ , g█▓       ,▓██,     ▓█        @▓▓╜╙╙▓
                  `    ▓█    ]▓█ ▓▓    ▄█▓"           ▓▓██▓╜       ,▓█Ñ▀█     ▓█        ▓▓▓,
                        ▓   ▓▓▓▄╖╢▓▄   ▓▓             ▓██▓╖       g▓▄╢╖╓▓▓    ▓▓          ▐▀▓▓
                 ╓     ╫▓  ▓█▀▀▀▀▀▀█W  ▓█W         , ╓▓░╝Ü▓█W    ╓▓▀▀▀▀▀▀▀▓   ▓█             ▐▓Ñ
                 ╙▓██▓▓▓╝ ▓▓        ▓▄  ╜╩▓███▒&▓██╩ ▓█   `╨██▓ g▓╜       ▓▓  ▓██████▓▓   @▓███
                    ╙╙"   '         ²╙      "╙`      ╙╙                    ╙       ╙╙     ▐▓╩






                                    Team leader, Repo management, UI/UX, Colours:

                                        leothelion#0001 (@ponte-vecchio)








                         Battleship:                                       ConnectFour:

                    Sujith#4243 (@NoblySP)                          Waremono#2092 (@vguo2037)











                    Minesweeper & Tetris:                                    Snake:

                    hawkeye#0007 (@sapgan)                             aph#8103 (@aphkyle)










                                                    2048:

                                        GoatSleepWithMe#1028 (@edwin10151)
"""
)

mypad.addstr(credit_text)
mypad.refresh(mypad_pos, 0, 5, 5, 40, 120)

for _ in range(180):
    mypad_pos += 1
    mypad.refresh(mypad_pos, 0, 5, 5, 40, 120)
    time.sleep(0.2)

time.sleep(5.0)
