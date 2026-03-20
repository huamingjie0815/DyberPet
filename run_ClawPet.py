import sys
from sys import platform
import ctypes
from tendo import singleton
import os
from ClawPet.pet_widget import PetWidget
from ClawPet.notification import CPNote
from ClawPet.accessory import CPAccessory

from PySide6.QtWidgets import QApplication
from PySide6 import QtCore
from PySide6.QtCore import Qt, QLocale, QTimer, QDateTime, QDate, Signal, QTime

from qfluentwidgets import  FluentTranslator, setThemeColor
from ClawPet.ClawSettings.control_panel import MainPanel

try:
    size_factor = 1 #ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
except:
    size_factor = 1

import ClawPet.settings as settings


# For translation:
# pylupdate5 langs.pro
# lrelease langs.zh_CN.ts

# For .exe:
# Now we use pyinstaller 6.5.0
# pyinstaller --noconsole --icon="000.ico" --hidden-import="pynput.mouse._win32" --hidden-import="pynput.keyboard._win32" run_ClawPet.py

# For Mac:
# pyinstaller --windowed --icon 000.icns --add-data="res:res" --add-data="ClawPet:ClawPet" --hidden-import="pynput.mouse._darwin" --hidden-import="pynput.keyboard._darwin" run_ClawPet.py


class ClawPetApp(QApplication):
    date_changed = Signal(QDate)

    def __init__(self, *args, **kwargs):
        super(ClawPetApp, self).__init__(*args, **kwargs)

        self.setQuitOnLastWindowClosed(False)
        screens = self.screens()
        primary_screen = self.primaryScreen()

        if primary_screen in screens:
            screens.insert(0, screens.pop(screens.index(primary_screen)))
        else:
            screens.insert(0, primary_screen)

        # internationalization
        fluentTranslator = FluentTranslator(QLocale(settings.language_code))
        self.installTranslator(fluentTranslator)
        self.installTranslator(settings.translator)
        if settings.themeColor:
            setThemeColor(settings.themeColor)
        

        # Pet Object
        self.p = PetWidget(screens=screens)

        # Notification System
        self.note = CPNote()

        # Accessory System
        self.acc = CPAccessory()

        # System Panel
        self.panel = MainPanel()

        # Midnight Timer
        self.current_date = QDate.currentDate()
        self.set_midnight_timer()

        # Signal Links
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        # Main Widget - others
        self.p.setup_notification.connect(self.note.setup_notification)
        self.p.setup_bubbleText.connect(self.note.setup_bubbleText)
        self.p.change_note.connect(self.note.change_pet)
        self.p.close_bubble.connect(self.note.close_bubble)
        self.p.setup_acc.connect(self.acc.setup_accessory)
        self.p.move_sig.connect(self.acc.send_main_movement)
        self.p.move_sig.connect(self.note.send_main_movement)
        self.p.close_all_accs.connect(self.acc.closeAll)

        # MainPanel - settings
        self.panel.settingInterface.ontop_changed.connect(self.acc.ontop_changed)
        self.panel.settingInterface.scale_changed.connect(self.acc.reset_size_sig)
        self.panel.settingInterface.ontop_changed.connect(self.p.ontop_update)
        self.panel.settingInterface.scale_changed.connect(self.p.reset_size)
        self.panel.settingInterface.lang_changed.connect(self.p.lang_changed)
        self.p.change_note.connect(self.panel.settingInterface._update_scale)

        # Chat panel navigation
        self.p.show_chat.connect(self.panel.show_chat)
        self.p.change_note.connect(self.panel.chatInterface.on_pet_changed)

        # Appearance panel
        self.panel.appearanceInterface.appearance_changed.connect(self.p._change_pet)
        self.p.change_note.connect(self.panel.appearanceInterface.on_pet_changed)

        # Midnight Trigger
        self.date_changed.connect(self.p._mightEventTrigger)
    
    def set_midnight_timer(self):
        now = QDateTime.currentDateTime()
        midnight = QDateTime(QDate.currentDate().addDays(1), QTime(0, 0, 0))  # Next midnight
        msecs_until_midnight = now.msecsTo(midnight)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.check_date)
        self.timer.start(msecs_until_midnight)
    
    def check_date(self):
        new_date = QDate.currentDate()
        if new_date != self.current_date:
            self.current_date = new_date
            self.date_changed.emit(new_date)
        self.set_midnight_timer()  # Reset the timer for the next midnight


        


if platform == 'win32':
    basedir = ''
else:
    basedir = os.path.dirname(__file__)

if __name__ == '__main__':

    # Avoid multiple process
    try:
        me = singleton.SingleInstance()
    except:
        sys.exit()


    # Create App
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = ClawPetApp(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    sys.exit(app.exec())


