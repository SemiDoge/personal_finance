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


def log(type: Log, message: str = None):
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
        trace = inspect.stack()
        if message == None:
            message = build_trace(trace)
        else:
            message = f"[{inspect.stack()[1][3]}]: " + message

    print(foreground + f"[{ts}] {type}: {message}" + Style.RESET_ALL)


def build_trace(trace):
    main_idx = 0
    for i in range(len(trace)):
        if trace[i][3].find("main") != -1:
            main_idx = i
            break
        else:
            continue

    message = "["
    itr = 1
    for i in range(main_idx):
        if i != 0:
            message += f" <= {trace[itr][3]}"
            itr += 1
            continue

        message += f"{trace[itr][3]}"
        itr += 1

    message += "]"

    return message
