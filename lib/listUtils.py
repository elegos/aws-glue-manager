from typing import Any


def popValues(l: list, *values: Any) -> bool:
    '''Returns True if any of the values are in the list'''
    found = False

    try:
        for value in values:
            l.remove(value)
            found = True
    except ValueError:
        pass

    return found
