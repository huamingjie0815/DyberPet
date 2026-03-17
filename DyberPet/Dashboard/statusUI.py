# coding:utf-8
import os
import json
import random

from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, HyperlinkCard, InfoBar,
                            ComboBoxSettingCard, ScrollArea, ExpandLayout, InfoBarPosition,
                            PushButton, TransparentToolButton, MessageBox, LineEdit, BodyLabel)

from qfluentwidgets import FluentIcon as FIF
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, QLocale, QSize
from PySide6.QtGui import QDesktopServices, QIcon, QImage
from PySide6.QtWidgets import QWidget, QLabel, QApplication, QSpacerItem, QSizePolicy, QHBoxLayout

from .dashboard_widgets import NoteFlowGroup, StatusCard

import DyberPet.settings as settings
import os
from sys import platform
basedir = settings.BASEDIR
module_path = os.path.join(basedir, 'DyberPet/Dashboard/')


class statusInterface(ScrollArea):
    """ Character status and logs interface (精简版) """
    changePet = Signal(name='changePet')
    changeStatus = Signal(str, int, str, name='changeStatus')

    def __init__(self, sizeHintdb: tuple[int, int], parent=None):
        super().__init__(parent=parent)
        self.setObjectName("statusInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.headerWidget = QWidget(self)
        self.headerWidget.setFixedWidth(sizeHintdb[0]-165)
        self.panelLabel = QLabel(self.tr("Status"), self.headerWidget)
        self.panelLabel.setSizePolicy(QSizePolicy.Maximum, self.panelLabel.sizePolicy().verticalPolicy())
        self.panelLabel.adjustSize()
        self.panelHelp = TransparentToolButton(QIcon(os.path.join(basedir, 'res/icons/question.svg')), self.headerWidget)
        self.panelHelp.setFixedSize(25,25)
        self.panelHelp.setIconSize(QSize(25,25))

        self.usertagLabel = BodyLabel(self.tr("User Name"))
        self.usertagLabel.setSizePolicy(QSizePolicy.Maximum, self.usertagLabel.sizePolicy().verticalPolicy())
        self.usertagEdit = LineEdit(self)
        self.usertagEdit.setClearButtonEnabled(True)
        self.usertagEdit.setPlaceholderText("")
        self.usertagEdit.setFixedWidth(150)
        usertag = settings.usertag_dict.get(settings.petname, "")
        self.usertagEdit.setText(usertag)

        self.headerLayout = QHBoxLayout(self.headerWidget)
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.setSpacing(0)

        self.headerLayout.addWidget(self.panelLabel, Qt.AlignLeft | Qt.AlignVCenter)
        spacerItem1 = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.headerLayout.addItem(spacerItem1)
        self.headerLayout.addWidget(self.panelHelp, Qt.AlignLeft | Qt.AlignVCenter)
        spacerItem2 = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.headerLayout.addItem(spacerItem2)
        self.headerLayout.addWidget(self.usertagLabel, Qt.AlignLeft | Qt.AlignVCenter)
        spacerItem3 = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.headerLayout.addItem(spacerItem3)
        self.headerLayout.addWidget(self.usertagEdit, Qt.AlignLeft | Qt.AlignVCenter)

        self.StatusCard = StatusCard(self)
        self.noteStream = NoteFlowGroup(self.tr('Status Log'), sizeHintdb, self.scrollWidget)

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 270, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.headerWidget.move(60, 20)
        self.StatusCard.move(60, 75)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(70, 30, 70, 0)
        self.expandLayout.addWidget(self.noteStream)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.panelLabel.setObjectName('panelLabel')

        theme = 'light'
        with open(os.path.join(basedir, 'res/icons/Dashboard/qss/', theme, 'status_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.panelHelp.clicked.connect(self._showInstruction)
        self.changePet.connect(self.StatusCard._changePet)
        self.usertagEdit.textChanged.connect(self._on_UserTag_changed)

    def _changePet(self):
        self.changePet.emit()
        usertag = settings.usertag_dict.get(settings.petname, "")
        self.usertagEdit.setText(usertag)

    def _addNote(self, icon, content):
        self.noteStream.addNote(icon, content)

    def _showInstruction(self):
        title = self.tr("Status Guide")
        content = self.tr("""Status Panel is about character status (精简版).

From top to bottom, there are 2 widgets:
⏺ Character Status

⏺ Notification Log
    - Don't worry if you missed any notification, all the notes will be saved here.
    ⚠️ But once you close the App, notes will be gone.""")
        self.__showMessageBox(title, content)
        return

    def __showMessageBox(self, title, content, yesText='OK'):
        WarrningMessage = MessageBox(title, content, self)
        if yesText == 'OK':
            WarrningMessage.yesButton.setText(self.tr('OK'))
        else:
            WarrningMessage.yesButton.setText(yesText)
        WarrningMessage.cancelButton.setText(self.tr('Cancel'))
        if WarrningMessage.exec():
            return True
        else:
            return False

    def _on_UserTag_changed(self, text):
        settings.usertag_dict[settings.petname] = text
        settings.save_settings()
