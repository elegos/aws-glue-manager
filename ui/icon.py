from PyQt5.QtGui import QIcon

from os import path


class QSVGIcon(QIcon):
    def __init__(self, fileName: str, *args, **kwargs) -> None:
        basePath = path.dirname(path.realpath(__file__))
        super().__init__(path.sep.join(
            [basePath, 'icons', fileName]), *args, **kwargs)
