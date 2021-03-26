from typing import List, Optional, Tuple
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget


class QTermDescription(QWidget):
    definitions: List[Tuple[str, str]]

    def __init__(self, definitions: List[Tuple[str, str]] = [], size: Optional[QSize] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.definitions = definitions

        layout = QGridLayout()
        self.setLayout(layout)

        if size != None:
            self.setSize(size)

        self._draw()

    def addDefinitions(self, definitions: List[Tuple[str, str]]):
        for definition in definitions:
            index = None
            for i in range(len(self.definitions)):
                if self.definitions[i][0] == definition[0]:
                    index = i
                    break

            if index == None:
                self.definitions.append(definition)
            else:
                self.definitions[index] = definition

        self._draw()

    def addDefinition(self, definition: Tuple[str, str]):
        index = None
        for i in range(len(self.definitions)):
            if self.definitions[i][0] == definition[0]:
                index = i
                break

        if index == None:
            self.definitions.append(definition)
        else:
            self.definitions[index] = definition

        self._draw()

    def removeDefinition(self, term: str):
        current = next(
            (defi for defi in self.definitions if defi[0] == term), None)

        if current != None:
            self.definitions.remove(current)

        self._draw()

    def _draw(self):
        layout: QGridLayout = self.layout()

        # Clean the previous graphical state
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

        for row in range(len(self.definitions)):
            definition = self.definitions[row]

            term = QLabel(f'{definition[0]}: ')
            termFont = QFont()
            termFont.setBold(True)
            term.setFont(termFont)
            defi = QLabel(definition[1])
            defi.setToolTip(definition[1])

            layout.addWidget(term, row, 0)
            layout.addWidget(defi, row, 1)
