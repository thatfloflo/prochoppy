"""Convenient CLI utility wrapper built on colorama.

This cli utility builds on colorama, but for convenience offers a set of functions
for writing, resetting ("rewinding") lines etc. and to use an SGML-based (HTML-like)
mark-up instead of having to manually place ANSI codes or the colorama placeholders
inside strings.
    
The Mini-Language used by this utility's functions supports four tags:
    - "<b COL>DATA</b>" is approx. equivalent to f"{Back.COL}DATA{Back.RESET}".
    - "<f COL>DATA</b>" is approx. equivalent to f"{Fore.COL}DATA{Fore.RESET}".
    - "<s ATTR>DATA</b> is approx. equivalent to f"{Style.ATTR}DATA{Style.RESET_ALL}".
    - "<br />" is converted to a newline.

As opposed to the simplicity of using the RESET option above, the markup parser
is a bit smarter and actually keeps track of what the settings for Back, Fore, and
Style were before the closing tag, then does what it has to in order to revert to
the previous state.

Like HTML, whitespace is collapsed to a single occurence and newlines are ignored
(use <br /> or <br> to effect a newline).
"""
from colorama import Fore, Back, Style, init as init_colorama
from html import escape as html_escape
from html.parser import HTMLParser

__all__ = ["init", "convert", "writeln", "newln", "write", "clearln", "ColoramaMLParser"]

class ColoramaMLParser(HTMLParser):
    """An SGML parser for HTML-like markup of colorama strings.
    """

    # Class attributes
    fores = {
        'black':    Fore.BLACK,
        'red':      Fore.RED,
        'green':    Fore.GREEN,
        'yellow':   Fore.YELLOW,
        'blue':     Fore.BLUE,
        'magenta':  Fore.MAGENTA,
        'cyan':     Fore.CYAN,
        'white':    Fore.WHITE,
        'reset':    Fore.RESET
    }
    backs = {
        'black':    Back.BLACK,
        'red':      Back.RED,
        'green':    Back.GREEN,
        'yellow':   Back.YELLOW,
        'blue':     Back.BLUE,
        'magenta':  Back.MAGENTA,
        'cyan':     Back.CYAN,
        'white':    Back.WHITE,
        'reset':    Back.RESET
    }
    styles = {
        'dim':      Style.DIM,
        'normal':   Style.NORMAL,
        'bright':   Style.BRIGHT,
        'reset':    Style.RESET_ALL
    }

    # Instance attributes
    _current_fore: str
    _current_back: str
    _current_style: str
    _fore_queue: list[str]
    _back_queue: list[str]
    _style_queue: list[str]
    _output_buffer: list[str]

    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.clear_buffer()

    def get_buffer(self) -> str:
        return "".join(self._output_buffer)

    def clear_buffer(self):
        self._current_fore: str = self.fores["reset"]
        self._current_back: str = self.backs["reset"]
        self._current_style: str = self.styles["reset"]
        self._output_buffer = []
        self._fore_queue = []
        self._back_queue = []
        self._style_queue = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            self._output_buffer.append("\n")
        elif tag == "b":
            for k, v in attrs:
                if k in self.backs:
                    self._back_queue.append(self._current_back)
                    self._current_back = self.backs[k]
                    self._output_buffer.append(self._current_back)
        elif tag == "f":
            for k, v in attrs:
                if k in self.fores:
                    self._fore_queue.append(self._current_fore)
                    self._current_fore = self.fores[k]
                    self._output_buffer.append(self._current_fore)
        elif tag == "s":
            for k, v in attrs:
                if k in self.styles:
                    self._style_queue.append(self._current_style)
                    self._current_style = self.styles[k]
                    self._output_buffer.append(self._current_style)
        else:
            attrlist: list[str] = []
            for k, v in attrs:
                if v is None:
                    attrlist.append(k)
                else:
                    attrlist.append(f'{k}="{html_escape(v)}"')
            attrstr = " ".join(attrlist)
            if attrstr:
                self._output_buffer.append(f"<{tag} {attrstr}>")
            else:
                self._output_buffer.append(f"<{tag}>")

    def handle_data(self, data: str) -> None:
        # if len(data.lstrip()) < len(data):
        #     self._output_buffer.append(" ")
        # self._output_buffer.append(data.strip())
        # if len(data.rstrip()) < len(data):
        #     self._output_buffer.append(" ")
        self._output_buffer.append(data.strip("\r\n"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "br":
            pass
        elif tag == "b":
            back = self._back_queue.pop() if len(self._back_queue) else self.backs["reset"]
            self._current_back = back
            self._output_buffer.append(back)
        elif tag == "f":
            fore = self._fore_queue.pop() if len(self._fore_queue) else self.fores["reset"]
            self._current_fore = fore
            self._output_buffer.append(fore)
        elif tag == "s":
            style = self._style_queue.pop() if len(self._style_queue) else self.styles["reset"]
            self._current_style = style
            self._output_buffer.append(style)
            self._output_buffer.append(self._current_back)
            self._output_buffer.append(self._current_fore)
        else:
            self._output_buffer.append(f"</{tag}>")

def init():
    """Initialise the cli util (will call colorama.init())."""
    init_colorama()


def convert(x: str) -> str:
    """Convert a string with xml-ified colorama markup to colorama string."""
    if "<" not in x or ">" not in x:
        return x
    parser = ColoramaMLParser()
    parser.feed(x)
    return parser.get_buffer()


def writeln(*args: str, sep: str =" ", convert_: bool = True):
    """Convert one or more strings and print them, followed by newline."""
    write(sep.join(args), sep="", convert_ = convert_)
    newln()


def newln():
    """Print newline and forcibly flush output."""
    print("\n", sep="", end="", flush=True)


def write(*args: str, sep: str = " ", convert_: bool = True):
    """Print args to output"""
    if convert_:
        print(convert(sep.join(args)), sep="", end="")
    else:
        print(sep.join(args), sep="", end="")


def clearln():
    """Erase current line and go back to its start."""
    print("\033[2K\r", sep="", end="", flush=True)
    #  write("\033[2K\033[1G")  # Not on Windows?
