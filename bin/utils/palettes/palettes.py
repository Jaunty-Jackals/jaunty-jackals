from math import ceil
from typing import Any


class Palette:
    """Basic class for setting up a colour palette"""

    def __init__(self):
        self.name = None
        self.number = (
            "color00",
            "color01",
            "color02",
            "color03",
            "color04",
            "color05",
            "color06",
            "color07",
            "color08",
            "color09",
            "color10",
            "color11",
            "color12",
            "color13",
            "color14",
            "color15",
            "foreground",
            "background",
        )
        self.alias = [
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "brightblack",
            "brightred",
            "brightgreen",
            "brightyellow",
            "brightblue",
            "brightmagenta",
            "brightcyan",
            "brightwhite",
            "foreground",
            "background",
        ]
        self.hex = [None] * 18
        assert len(self.number) == len(self.alias) == len(self.hex)

        self.palette = {"number": self.number, "alias": self.alias, "hex": self.hex}

    def to_hex(self, term: str, sharp: bool = False):
        """Searches up the term from palette and returns a hex code for a given colour."""
        assert len(self.number) == len(self.alias) == len(self.hex)
        assert isinstance(term, str) and isinstance(sharp, bool)
        prefix = ""
        if sharp is True:
            prefix = "#"
        if term in self.palette["number"]:
            for element in range(len(self.palette["number"])):
                if self.palette["number"][element] == term.lower():
                    return f'{prefix}{self.palette["hex"][element]}'
        elif term in self.palette["alias"]:
            for element in range(len(self.palette["alias"])):
                if self.palette["alias"][element] == term.lower():
                    return f'{prefix}{self.palette["hex"][element]}'
        elif term in self.palette["hex"]:
            return f"{prefix}{term}"
        else:
            raise ValueError("Specified colour does not exist.")

    def to_rgb(self, term: str, curses: bool = False) -> tuple:
        """Returns a tuple of RGB values for a given colour number, alias or HEX code"""
        assert isinstance(term, str) and isinstance(curses, bool)
        if term in self.palette["number"]:
            for element in range(len(self.palette["number"])):
                if self.palette["number"][element] == term.lower():
                    if curses is False:
                        return tuple(
                            int(self.palette["hex"][element][i : i + 2], 16)
                            for i in (0, 2, 4)
                        )
                    elif curses is True:
                        rgb = tuple(
                            int(self.palette["hex"][element][i : i + 2], 16)
                            for i in (0, 2, 4)
                        )
                        return tuple(ceil(rgb[k] / 255 * 1000) for k in range(3))
        elif term in self.palette["alias"]:
            for element in range(len(self.palette["alias"])):
                if self.palette["alias"][element] == term.lower():
                    if curses is False:
                        return tuple(
                            int(self.palette["hex"][element][i : i + 2], 16)
                            for i in (0, 2, 4)
                        )
                    elif curses is True:
                        rgb = tuple(
                            int(self.palette["hex"][element][i : i + 2], 16)
                            for i in (0, 2, 4)
                        )
                        return tuple(ceil(rgb[k] / 255 * 1000) for k in range(3))
        elif term in self.palette["hex"]:
            if curses is False:
                return tuple(
                    int(self.palette["hex"][term][i : i + 2], 16) for i in (0, 2, 4)
                )
            elif curses is True:
                rgb = tuple(
                    int(self.palette["hex"][term][i : i + 2], 16) for i in (0, 2, 4)
                )
                return tuple(ceil(rgb[k] / 255 * 1000) for k in range(3))
        elif "#" in term:
            rgb_term = term.lstrip("#")
            if rgb_term in self.palette["hex"]:
                if curses is False:
                    return tuple(
                        int(self.palette["hex"][rgb_term][i : i + 2], 16)
                        for i in (0, 2, 4)
                    )
                elif curses is True:
                    rgb = tuple(
                        int(self.palette["hex"][rgb_term][i : i + 2], 16)
                        for i in (0, 2, 4)
                    )
                    return tuple(ceil(rgb[k] / 255 * 1000) for k in range(3))
        else:
            raise ValueError(
                "Specified colour does not exist in the palette, therefore cannot convert to RGB format."
            )

    def to_curses_rgb(self, term: str, component: str) -> int:
        """Returns an integer corresponding to curses' colourcoding of 0 ~ 1000 for a RGB colour component"""
        assert (
            isinstance(term, str)
            and isinstance(component, str)
            and component.upper() in ("R", "G", "B")
        )
        if term in self.palette["number"]:
            for element in range(len(self.palette["number"])):
                if self.palette["number"][element] == term.lower():
                    rgb = tuple(
                        int(self.palette["hex"][element][i : i + 2], 16)
                        for i in (0, 2, 4)
                    )
                    if component.upper() in "R":
                        return ceil(rgb[0] / 255 * 1000)
                    elif component.upper() in "G":
                        return ceil(rgb[1] / 255 * 1000)
                    else:
                        return ceil(rgb[2] / 255 * 1000)
        elif term in self.palette["alias"]:
            for element in range(len(self.palette["alias"])):
                if self.palette["alias"][element] == term.lower():
                    rgb = tuple(
                        int(self.palette["hex"][element][i : i + 2], 16)
                        for i in (0, 2, 4)
                    )
                    if component.upper() in "R":
                        return ceil(rgb[0] / 255 * 1000)
                    elif component.upper() in "G":
                        return ceil(rgb[1] / 255 * 1000)
                    else:
                        return ceil(rgb[2] / 255 * 1000)
        elif term in self.palette["hex"]:
            rgb = tuple(int(term[i : i + 2], 16) for i in (0, 2, 4))
            if component.upper() in "R":
                return ceil(rgb[0] / 255 * 1000)
            elif component.upper() in "G":
                return ceil(rgb[1] / 255 * 1000)
            else:
                return ceil(rgb[2] / 255 * 1000)
        elif "#" in term:
            rgb_term = term.lstrip("#")
            if term in self.palette["hex"]:
                rgb = tuple(int(rgb_term[i : i + 2], 16) for i in (0, 2, 4))
                if component.upper() in "R":
                    return ceil(rgb[0] / 255 * 1000)
                elif component.upper() in "G":
                    return ceil(rgb[1] / 255 * 1000)
                else:
                    return ceil(rgb[2] / 255 * 1000)
        else:
            raise ValueError(
                "Specified colour does not exist in the palette, therefore cannot convert to curses RGB format."
            )

    def to_greyscale(self, colour: str, out: str = "RGB", sharp: bool = False) -> Any:
        """Converts a given colour (RGB or HEX) to a greyscaled colour"""
        assert isinstance(out, str) and out.upper() in ["RGB", "HEX"]
        assert isinstance(colour, tuple) or isinstance(colour, str)
        greyscale_factor = (0.3, 0.59, 0.11)
        prefix = ""
        if out.upper() == "RGB":
            sharp = False
        if sharp is True:
            prefix = "#"

        # TODO: RGB -> out
        if isinstance(colour, tuple) and len(colour) == 3:
            if out.upper() == "RGB":
                return (
                    int(sum(colour[i] * greyscale_factor[i] for i in range(3))),
                ) * 3
            else:
                out_hex = "%02X%02X%02X" % tuple([int(spec) for spec in colour[:3]])
                return f"{prefix}{out_hex}"

        # TODO: HEX -> out
        if isinstance(colour, str):
            if "#" in colour and len(colour) == 7:
                colour_ = colour.lstrip("#")
                colour_rgb = tuple(int(colour_[i : i + 2], 16) for i in (0, 2, 4))
                return self.to_greyscale(colour_rgb, out=out, sharp=sharp)

            elif len(colour) == 6:
                colour_rgb = tuple(int(colour[i : i + 2], 16) for i in (0, 2, 4))
                return self.to_greyscale(colour_rgb, out=out, sharp=sharp)

    def __str__(self):
        return f"{self.name} palette containing {len(self.hex)} colours"

    def __repr__(self):
        return f"{type(self.palette)}"


class Base16(Palette):
    """Object for Base16 3024 Theme"""

    def __init__(self):
        super().__init__()
        self.name = "Base16 3024"
        self.hex = [
            "090300",  # 00
            "DB2D20",  # 01
            "01A252",  # 02
            "FDED02",  # 03
            "01A0E4",  # 04
            "A16A94",  # 05
            "B5E4F4",  # 06
            "A5A2A2",  # 07
            "5C5855",  # 08
            "DB2D20",  # 01 09
            "01A252",  # 02 10
            "FDED02",  # 03 11
            "01A0E4",  # 04 12
            "A16A94",  # 05 13
            "B5E4F4",  # 06 14
            "F7F7F7",  # 07 15
            "A5A2A2",  # fg
            "090300",  # bg
        ]
        self.palette = {
            "name": self.name,
            "number": self.number,
            "alias": self.alias,
            "hex": self.hex,
        }


class Nord(Palette):
    """Object class for Nord Theme"""

    def __init__(self):
        super().__init__()
        self.name = "Nord"
        self.hex = [
            "2e3440",  # 00
            "3b4252",  # 01
            "434c5e",  # 02
            "4c566a",  # 03
            "d8dee9",  # 04
            "e5e9f0",  # 05
            "eceff4",  # 06
            "8fbcbb",  # 07
            "88c0d0",  # 08
            "81a1c1",  # 09
            "5e81ac",  # 10
            "bf616a",  # 11
            "d08770",  # 12
            "ebcb8b",  # 13
            "a3be8c",  # 14
            "b48ead",  # 15
            "eceff4",  # fg
            "2e3440",
        ]  # bg

        self.palette = {"number": self.number, "alias": self.alias, "hex": self.hex}


class Dracula(Palette):
    """Dracula theme

    Credit to https://github.com/dracula
    """

    def __init__(self):
        super().__init__()
        self.name = "Dracula"
        self.hex = [
            "22222C",  # 00
            "EB675A",  # 01
            "87F684",  # 02
            "F6CE76",  # 03
            "8DA7FB",  # 04
            "C094E7",  # 05
            "A4E5FB",  # 06
            "F8F8F3",  # 07
            "545454",  # 08
            "EC7A72",  # 09
            "95FB9B",  # 10
            "F6CE76",  # 11
            "D0ADFC",  # 12
            "F099DD",  # 13
            "BAFBFE",  # 14
            "BAFBFE",  # 15
            "F8F8F3",  # fg = 07
            "22222C",  # bg = 00
        ]
        self.palette = {
            "name": self.name,
            "number": self.number,
            "alias": self.alias,
            "hex": self.hex,
        }


class Gruvbox(Palette):
    """Gruvbox theme

    Credit to https://github.com/morhetz/gruvbox
    """

    def __init__(self):
        super().__init__()
        self.name = "Gruvbox"
        self.hex = [
            "282828",  # 00
            "BA3C28",  # 01
            "98972F",  # 02
            "CD9D37",  # 03
            "578287",  # 04
            "A66786",  # 05
            "749B6D",  # 06
            "A59A85",  # 07
            "908476",  # 08
            "E65D3E",  # 09
            "B8BB3E",  # 10
            "F0C148",  # 11
            "8BA398",  # 12
            "C88B9B",  # 13
            "99BE81",  # 14
            "E8DCB5",  # 15
            "E8DCB5",  # fg = 15
            "282828",  # bg = 00
        ]
        self.palette = {
            "name": self.name,
            "number": self.number,
            "alias": self.alias,
            "hex": self.hex,
        }


class Commodore64(Palette):
    """Commodore64 theme"""

    def __init__(self):
        super().__init__()
        self.name = "Commodore64"
        self.hex = [
            "51469B",  # 00
            "915244",  # 01
            "76AA61",  # 02
            "CCD58B",  # 03
            "51469B",  # 04
            "955BA4",  # 05
            "8BBFC8",  # 06
            "FFFFFF",  # 07
            "51469B",  # 00 08
            "915244",  # 01 09
            "76AA61",  # 02 10
            "CCD58B",  # 03 11
            "51469B",  # 04 12
            "955BA4",  # 05 13
            "8BBFC8",  # 06 14
            "FFFFFF",  # 07 15
            "FFFFFF",  # fg = 07 unique
            "51469B",  # bg = 04
        ]
        self.palette = {
            "name": self.name,
            "number": self.number,
            "alias": self.alias,
            "hex": self.hex,
        }


class Haxx0r(Palette):
    """Haxx0r theme"""

    def __init__(self):
        super().__init__()
        self.name = "Haxx0r"
        self.hex = [
            "000000",  # 00
            "00FF00",  # 01
            "00EE00",  # 02
            "00DD00",  # 03
            "00CC00",  # 04
            "00AA00",  # 05
            "009900",  # 06
            "008800",  # 07
            "000000",  # 00
            "00FF00",  # 01
            "00EE00",  # 02
            "00DD00",  # 03
            "00CC00",  # 04
            "00AA00",  # 05
            "009900",  # 06
            "008800",  # 07
            "00FF00",  # fg = 07 unique
            "000000",  # bg = 04
        ]
        self.palette = {
            "name": self.name,
            "number": self.number,
            "alias": self.alias,
            "hex": self.hex,
        }


class Jackal(Palette):
    """Jackal theme"""

    def __init__(self):
        super().__init__()
        self.name = "Jackal"
        self.hex = [
            "1f1f1f",  # 00
            "d17b49",  # 01
            "7b8748",  # 02
            "af865a",  # 03
            "535c5c",  # 04
            "775759",  # 05
            "6d715e",  # 06
            "C0B18B",  # 07
            "4a3637",  # 00 08
            "d17b49",  # 01 09
            "7b8748",  # 02 10
            "af865a",  # 03 11
            "535c5c",  # 04 12
            "775759",  # 05 13
            "6d715e",  # 06 14
            "C0B18B",  # 07 15
            "C0B18B",  # fg = 07 unique
            "1F1F1F",  # bg = 04
        ]
        self.palette = {
            "name": self.name,
            "number": self.number,
            "alias": self.alias,
            "hex": self.hex,
        }
