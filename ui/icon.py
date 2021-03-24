from PyQt5.QtGui import QIcon

from os import path


class QSVGIcon(QIcon):
    def __init__(self, fileName: str, *args, **kwargs) -> None:
        super().__init__(path.sep.join(
            ['ui', 'icons', fileName]), *args, **kwargs)
