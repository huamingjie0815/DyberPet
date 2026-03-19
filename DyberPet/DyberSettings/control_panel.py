# coding:utf-8
import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow
from qfluentwidgets import FluentIcon as FIF

from .basic_setting_ui import SettingInterface
from .chat_ui import ChatInterface
import DyberPet.settings as settings
basedir = settings.BASEDIR


class MainPanel(FluentWindow):

    def __init__(self, minWidth=800, minHeight=800):
        super().__init__()

        self.chatInterface = ChatInterface(sizeHintDyber=(minWidth, minHeight), parent=self)
        self.settingInterface = SettingInterface(self)

        self.initNavigation()
        self.setMinimumSize(minWidth, minHeight)
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.chatInterface, FIF.CHAT, self.tr('Chat'))
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Settings'))
        self.navigationInterface.setExpandWidth(200)

    def initWindow(self):
        self.setWindowIcon(QIcon(os.path.join(basedir, "res/icons/SystemPanel.png")))
        self.setWindowTitle(self.tr('DyberPet'))
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def show_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def show_chat(self):
        self.show()
        self.stackedWidget.setCurrentWidget(self.chatInterface)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
