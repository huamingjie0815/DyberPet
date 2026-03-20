# coding:utf-8
import os
import json
import shutil

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                               QScrollArea, QFileDialog, QInputDialog,
                               QMessageBox, QSizePolicy, QFrame)

from qfluentwidgets import (ScrollArea, ExpandLayout, PushButton, PrimaryPushButton,
                            CardWidget, CaptionLabel, BodyLabel, SubtitleLabel,
                            InfoBar, InfoBarPosition, FluentIcon as FIF)

import ClawPet.settings as settings

basedir = settings.BASEDIR
ROLE_DIR = os.path.join(basedir, 'res/role')

REQUIRED_FILES = ['pet_conf.json', 'act_conf.json']
REQUIRED_DIRS = ['action']

_MINIMAL_PET_CONF = {
    "width": 128,
    "height": 128,
    "scale": 1.0,
    "refresh": 5,
    "interact_speed": 0.02,
    "default": "default",
    "up": "default",
    "down": "default",
    "left": "default",
    "right": "default",
    "drag": "default",
    "fall": "default",
    "on_floor": "default",
    "random_act": [
        {"name": "idle", "act_list": ["default"], "act_prob": 1.0, "act_type": [2, 0]}
    ],
    "accessory_act": [],
    "patpat": "default"
}

_MINIMAL_ACT_CONF = {
    "default": {
        "images": "stand",
        "act_num": 1
    }
}


def _get_thumbnail(pet_name: str):
    """Return first frame of the default action as QPixmap, or None."""
    try:
        conf_path = os.path.join(ROLE_DIR, pet_name, 'act_conf.json')
        act_conf = json.load(open(conf_path, 'r', encoding='UTF-8'))
        images_key = act_conf.get('default', {}).get('images', '')
        action_dir = os.path.join(ROLE_DIR, pet_name, 'action')
        for ext in ('.png', '.gif'):
            img_path = os.path.join(action_dir, f'{images_key}_0{ext}')
            if os.path.isfile(img_path):
                return QPixmap(img_path)
        # fallback: first png in action dir
        for fname in sorted(os.listdir(action_dir)):
            if fname.endswith('.png'):
                return QPixmap(os.path.join(action_dir, fname))
    except Exception:
        pass
    return None


def _validate_appearance_folder(folder: str):
    """Return error string if folder is invalid, else None."""
    for f in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(folder, f)):
            return f'Missing required file: {f}'
    for d in REQUIRED_DIRS:
        if not os.path.isdir(os.path.join(folder, d)):
            return f'Missing required folder: {d}/'
    return None


class AppearanceCard(QFrame):
    """Single appearance row card."""

    switch_requested = Signal(str)

    def __init__(self, pet_name: str, is_current: bool, parent=None):
        super().__init__(parent=parent)
        self.pet_name = pet_name
        self.setObjectName('AppearanceCard')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        if is_current:
            self.setStyleSheet("""
                AppearanceCard {
                    background: #EEF4FF;
                    border: 1.5px solid #6CA0DC;
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                AppearanceCard {
                    background: #FAF9F8;
                    border: 1px solid #E0D8D0;
                    border-radius: 10px;
                }
            """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Thumbnail
        thumb_label = QLabel()
        thumb_label.setFixedSize(56, 56)
        thumb_label.setAlignment(Qt.AlignCenter)
        pixmap = _get_thumbnail(pet_name)
        if pixmap and not pixmap.isNull():
            thumb_label.setPixmap(pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            thumb_label.setText('?')
            thumb_label.setStyleSheet('color: #aaa; font-size: 24px;')
        layout.addWidget(thumb_label)

        # Name + status
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        name_label = BodyLabel(pet_name)
        name_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        info_layout.addWidget(name_label)
        if is_current:
            status_label = CaptionLabel(self.tr('Current'))
            status_label.setStyleSheet('color: #6CA0DC;')
            info_layout.addWidget(status_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        layout.addStretch()

        # Switch button
        if not is_current:
            btn = PushButton(self.tr('Switch'))
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda: self.switch_requested.emit(self.pet_name))
            layout.addWidget(btn)
        else:
            spacer = QWidget()
            spacer.setFixedWidth(80)
            layout.addWidget(spacer)


class AppearanceInterface(ScrollArea):
    """Appearance management panel: list, switch, import, create."""

    appearance_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('AppearanceInterface')
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._root = QWidget()
        self._root.setObjectName('AppearanceRoot')
        self._root.setStyleSheet('QWidget#AppearanceRoot { background: transparent; }')
        self.setWidget(self._root)

        self._layout = QVBoxLayout(self._root)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(16)
        self.setStyleSheet('QScrollArea { background: transparent; border: none; }')

        self._build_ui()

    def _build_ui(self):
        # Title
        title = SubtitleLabel(self.tr('Appearance Management'))
        self._layout.addWidget(title)

        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._import_btn = PrimaryPushButton(FIF.ADD, self.tr('Import Appearance'))
        self._import_btn.clicked.connect(self._import_appearance)
        btn_row.addWidget(self._import_btn)

        self._create_btn = PushButton(FIF.EDIT, self.tr('Create New'))
        self._create_btn.clicked.connect(self._create_appearance)
        btn_row.addWidget(self._create_btn)

        btn_row.addStretch()
        self._layout.addLayout(btn_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet('color: #E0D8D0;')
        self._layout.addWidget(sep)

        # Card list
        self._cards_widget = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(8)
        self._layout.addWidget(self._cards_widget)
        self._layout.addStretch()

        self._refresh_cards()

    def _refresh_cards(self):
        # Clear existing cards
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current = settings.petname or settings.default_pet
        pets = settings.pets
        for pet_name in pets:
            card = AppearanceCard(pet_name, pet_name == current)
            card.switch_requested.connect(self._on_switch)
            self._cards_layout.addWidget(card)

    def _on_switch(self, pet_name: str):
        self.appearance_changed.emit(pet_name)
        # Update current marker without waiting for signal round-trip
        QFrame.__init__  # just trigger refresh
        self._refresh_cards()

    def _import_appearance(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr('Select Appearance Folder'),
            basedir,
        )
        if not folder:
            return

        err = _validate_appearance_folder(folder)
        if err:
            InfoBar.error(
                title=self.tr('Invalid Appearance'),
                content=err,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self,
            )
            return

        pet_name = os.path.basename(folder.rstrip('/\\'))
        dest = os.path.join(ROLE_DIR, pet_name)
        if os.path.exists(dest):
            reply = QMessageBox.question(
                self,
                self.tr('Overwrite?'),
                self.tr(f'Appearance "{pet_name}" already exists. Overwrite?'),
            )
            if reply != QMessageBox.Yes:
                return
            shutil.rmtree(dest)

        try:
            shutil.copytree(folder, dest)
        except Exception as e:
            InfoBar.error(
                title=self.tr('Import Failed'),
                content=str(e),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )
            return

        settings.reload_petlist()
        self._refresh_cards()
        InfoBar.success(
            title=self.tr('Imported'),
            content=self.tr(f'Appearance "{pet_name}" imported successfully.'),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def _create_appearance(self):
        name, ok = QInputDialog.getText(
            self,
            self.tr('New Appearance'),
            self.tr('Enter name for the new appearance (no spaces):'),
        )
        if not ok or not name.strip():
            return

        name = name.strip().replace(' ', '_')
        dest = os.path.join(ROLE_DIR, name)
        if os.path.exists(dest):
            InfoBar.warning(
                title=self.tr('Already Exists'),
                content=self.tr(f'Appearance "{name}" already exists.'),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            return

        try:
            os.makedirs(os.path.join(dest, 'action'), exist_ok=True)
            with open(os.path.join(dest, 'pet_conf.json'), 'w', encoding='UTF-8') as f:
                json.dump(_MINIMAL_PET_CONF, f, ensure_ascii=False, indent=2)
            with open(os.path.join(dest, 'act_conf.json'), 'w', encoding='UTF-8') as f:
                json.dump(_MINIMAL_ACT_CONF, f, ensure_ascii=False, indent=2)

            # Copy a placeholder image from Kitty so it's immediately loadable
            src_img = os.path.join(ROLE_DIR, 'Kitty', 'action', 'stand_0.png')
            if os.path.isfile(src_img):
                shutil.copy2(src_img, os.path.join(dest, 'action', 'stand_0.png'))
        except Exception as e:
            InfoBar.error(
                title=self.tr('Creation Failed'),
                content=str(e),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )
            return

        settings.reload_petlist()
        self._refresh_cards()

        # Open folder in Finder/Explorer so user can add their assets
        import subprocess, sys
        if sys.platform == 'darwin':
            subprocess.Popen(['open', dest])
        elif sys.platform == 'win32':
            subprocess.Popen(['explorer', dest])
        else:
            subprocess.Popen(['xdg-open', dest])

        InfoBar.success(
            title=self.tr('Created'),
            content=self.tr(f'Appearance "{name}" scaffolded. Add your images to the action/ folder.'),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )

    def on_pet_changed(self, pet_name: str = ''):
        """Called when the active pet changes externally (e.g. from right-click menu)."""
        self._refresh_cards()
