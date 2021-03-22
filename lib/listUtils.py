from typing import Any


def popFlag(l: list, *values: Any) -> bool:
    '''Returns True if any of the values are in the list'''
    found = False

    for value in values:
        try:
            l.remove(value)
            found = True
        except ValueError:
            pass

    return found
