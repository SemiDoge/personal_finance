import inspect
import datetime as dt

from colorama import init, Fore, Style
from enum import Enum

class Log(Enum):
    TRACE = 1
    DEBUG = 2
    INFO = 3
    WARNING = 4
    ERROR = 5

    def __str__(self):
        return self.name.lower()

def log(type: Log, message: str):
    init()

    foreground = Fore.RESET

    match type:
        case Log.TRACE:  
            foreground = Fore.GREEN
        case Log.DEBUG:
            foreground = Fore.LIGHTYELLOW_EX
        case Log.INFO:
            foreground = Fore.BLUE
        case Log.WARNING:
            foreground = Fore.YELLOW
        case Log.ERROR:
            foreground = Fore.RED
        case _:
            foreground = Fore.RESET

    ts = dt.datetime.now().strftime("%m/%d %H:%M:%S")
    if type == Log.TRACE:
        message = f"[{inspect.stack()[1][3]}]: " + message

    print(foreground + f"[{ts}] {type}: {message}" + Style.RESET_ALL)