import os
from colorama import Style, Fore


def bright(txt):
    return f"{Style.BRIGHT}{txt}{Style.RESET_ALL}"


def bgreen(txt):
    return f"{Fore.GREEN}{Style.BRIGHT}{txt}{Style.RESET_ALL}"


def bred(txt):
    return f"{Fore.RED}{Style.BRIGHT}{txt}{Style.RESET_ALL}"


def bmagenta(txt):
    return f"{Fore.MAGENTA}{Style.BRIGHT}{txt}{Style.RESET_ALL}"


def bblue(txt):
    return f"{Fore.BLUE}{Style.BRIGHT}{txt}{Style.RESET_ALL}"


def yellow(txt):
    return f"{Fore.YELLOW}{txt}{Style.RESET_ALL}"


def flatten(l):
    return [item for sublist in l for item in sublist]


def namify_player_list(plist):
    if isinstance(plist, list):
        for i, p in enumerate(plist):
            plist[i] = namify_player_list(p)
    else:
        plist = plist.name
    return plist
