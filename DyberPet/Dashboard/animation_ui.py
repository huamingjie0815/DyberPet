# coding:utf-8
import os

from qfluentwidgets import (ScrollArea, ExpandLayout, TransparentToolButton, MessageBox)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QVBoxLayout

import DyberPet.settings as settings
basedir = settings.BASEDIR


class animationInterface(ScrollArea):
    """ Character animations management interface """

    def __init__(self, sizeHintdb: tuple[int, int], parent=None):
        super().__init__(parent=parent)
        self.current_pet = settings.petname
        self.setObjectName("animationInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.headerWidget = QWidget(self)
        self.headerWidget.setFixedWidth(sizeHintdb[0]-165)
        self.panelLabel = QLabel(self.tr("Animation"), self.headerWidget)
        self.panelLabel.setSizePolicy(QSizePolicy.Maximum, self.panelLabel.sizePolicy().verticalPolicy())
        self.panelLabel.adjustSize()
        self.panelHelp = TransparentToolButton(QIcon(os.path.join(basedir, 'res/icons/question.svg')), self.headerWidget)
        self.panelHelp.setFixedSize(25,25)
        self.panelHelp.setIconSize(QSize(25,25))

        self.headerLayout = QHBoxLayout(self.headerWidget)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(0)

        self.headerLayout.addWidget(self.panelLabel, Qt.AlignLeft | Qt.AlignVCenter)
        spacerItem1 = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.headerLayout.addItem(spacerItem1)
        self.headerLayout.addWidget(self.panelHelp, Qt.AlignLeft | Qt.AlignVCenter)
        spacerItem2 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.headerLayout.addItem(spacerItem2)

        self.infoLabel = QLabel(self)
        self.infoLabel.setText(self.tr("Available animations for the current pet are shown in the action menu."))
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setStyleSheet("color: gray; padding: 10px;")

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 75, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.headerWidget.move(60, 20)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(70, 10, 70, 0)

        self.expandLayout.addWidget(self.infoLabel)

    def __setQss(self):
        self.scrollWidget.setObjectName('scrollWidget')
        self.panelLabel.setObjectName('panelLabel')

        theme = 'light'
        with open(os.path.join(basedir, 'res/icons/Dashboard/qss/', theme, 'status_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __connectSignalToSlot(self):
        self.panelHelp.clicked.connect(self._showInstruction)

    def _showInstruction(self):
        title = self.tr("Animation Panel Guide")
        content = self.tr("""In Animation Panel, you can
⏺ select an action to play from the pet's action menu
⏺ the pet will randomly perform actions from the playlist

📌About the random playlist:
The character will randomly do some action when not being interacted with
At different states, the behavior will be different""")
        WarrningMessage = MessageBox(title, content, self)
        WarrningMessage.yesButton.setText(self.tr('OK'))
        WarrningMessage.cancelButton.setText(self.tr('Cancel'))
        WarrningMessage.exec()
