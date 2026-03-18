# coding:utf-8
import sys
import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget,  SplitFluentWindow, FluentTranslator,
                            NavigationSeparator)
from qfluentwidgets import FluentIcon as FIF

from .basic_setting_ui import SettingInterface
from .game_save_ui import SaveInterface
from .char_card_ui import CharInterface
from .chat_ui import ChatInterface
from DyberPet.Dashboard.status_ui import statusInterface
from DyberPet.Dashboard.task_ui import taskInterface
from sys import platform
import DyberPet.settings as settings
basedir = settings.BASEDIR

module_path = os.path.join(basedir, 'DyberPet/DyberSettings/')


class ControlMainWindow(FluentWindow):

    def __init__(self, minWidth=800, minHeight=800):
        super().__init__()

        # create sub interface
        self.settingInterface = SettingInterface(self)
        self.gamesaveInterface = SaveInterface(sizeHintDyber=(minWidth, minHeight), parent=self)
        self.charCardInterface = CharInterface(sizeHintDyber=(minWidth, minHeight), parent=self)
        self.chatInterface = ChatInterface(sizeHintDyber=(minWidth, minHeight), parent=self)
        self.statusInterface = statusInterface(sizeHintdb=(minWidth, minHeight), parent=self)
        self.taskInterface = taskInterface(sizeHintdb=(minWidth, minHeight), parent=self)

        self.initNavigation()
        self.setMinimumSize(minWidth, minHeight)
        self.initWindow()

    def initNavigation(self):
        # add sub interface - grouped under one control panel
        self.addSubInterface(self.statusInterface,
                             QIcon(os.path.join(basedir, "res/icons/dashboard.svg")),
                             self.tr('Home'))
        self.addSubInterface(self.charCardInterface,
                             QIcon(os.path.join(basedir, "res/icons/system/character.svg")),
                             self.tr('Characters'))
        self.addSubInterface(self.taskInterface,
                             FIF.ALIGNMENT,
                             self.tr('Focus'))
        self.addSubInterface(self.gamesaveInterface,
                             FIF.SAVE,
                             self.tr('Save & Load'))
        self.addSubInterface(self.chatInterface,
                             FIF.CHAT,
                             self.tr('Chat'))
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Settings'))

        self.navigationInterface.setExpandWidth(200)

    def initWindow(self):
        self.setWindowIcon(QIcon(os.path.join(basedir, "res/icons/SystemPanel.png")))
        self.setWindowTitle(self.tr('System'))

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def show_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def show_chat(self):
        self.show()
        self.stackedWidget.setCurrentWidget(self.chatInterface)

    def show_dashboard(self):
        self.show()
        self.stackedWidget.setCurrentWidget(self.statusInterface)

    def closeEvent(self, event):
        event.ignore()  # Ignore the close event
        self.hide()
