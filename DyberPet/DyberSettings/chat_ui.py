# coding:utf-8
import os
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                               QScrollArea, QLineEdit, QPushButton, QSizePolicy,
                               QSpacerItem, QTextBrowser, QComboBox, QFrame)

from qfluentwidgets import FluentIcon as FIF, ExpandLayout
from qfluentwidgets import CaptionLabel, CardWidget

import DyberPet.settings as settings
basedir = settings.BASEDIR

CHAT_MESSAGE_MAX_WIDTH = 360

try:
    import markdown as _markdown_lib
    def _render_markdown(text: str) -> str:
        return _markdown_lib.markdown(text, extensions=['fenced_code', 'tables'])
except ImportError:
    def _render_markdown(text: str) -> str:
        import html
        return f"<p>{html.escape(text)}</p>"


_BUBBLE_USER_CSS = """
    body { margin:0; padding:0; background:transparent; }
    p { margin:0 0 4px 0; color: white; font-size:13px; }
    code { background: rgba(255,255,255,0.2); border-radius:3px; padding: 1px 4px; }
    pre { background: rgba(0,0,0,0.2); border-radius:6px; padding:8px; overflow-x:auto; }
    table { border-collapse:collapse; width:100%; }
    td, th { border: 1px solid rgba(255,255,255,0.3); padding:4px 8px; }
"""

_BUBBLE_PET_CSS = """
    body { margin:0; padding:0; background:transparent; }
    p { margin:0 0 4px 0; color: #333333; font-size:13px; }
    code { background: rgba(0,0,0,0.07); border-radius:3px; padding: 1px 4px; }
    pre { background: rgba(0,0,0,0.07); border-radius:6px; padding:8px; overflow-x:auto; }
    table { border-collapse:collapse; width:100%; }
    td, th { border: 1px solid #cccccc; padding:4px 8px; }
"""


class MarkdownBubble(QTextBrowser):
    def __init__(self, content: str, is_user: bool, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("markdownBubble")
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        css = _BUBBLE_USER_CSS if is_user else _BUBBLE_PET_CSS
        html_body = _render_markdown(content)
        self.setHtml(f"<style>{css}</style>{html_body}")

        if is_user:
            self.setStyleSheet("background: transparent; border: none; color: white;")
        else:
            self.setStyleSheet("background: transparent; border: none; color: #333333;")
        self._adjust_height()

    def set_content(self, content: str, is_user: bool):
        css = _BUBBLE_USER_CSS if is_user else _BUBBLE_PET_CSS
        html_body = _render_markdown(content)
        self.setHtml(f"<style>{css}</style>{html_body}")
        self._adjust_height()

    def _adjust_height(self):
        self.document().setTextWidth(CHAT_MESSAGE_MAX_WIDTH - 28)
        h = int(self.document().size().height()) + 10
        self.setFixedHeight(max(h, 30))


class ChatMessageWidget(QWidget):
    def __init__(self, sender: str, content: str, timestamp: datetime = None, parent=None):
        super().__init__(parent=parent)
        self.sender = sender
        self.is_user = sender == "user"
        self.timestamp = timestamp or datetime.now()
        self._content = content

        self._init_ui()

    def _init_ui(self):
        self.setFixedWidth(CHAT_MESSAGE_MAX_WIDTH + 40)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(12, 8, 12, 8)
        self.hBoxLayout.setSpacing(8)

        bubble = CardWidget(self)
        bubble.setFixedWidth(CHAT_MESSAGE_MAX_WIDTH)
        bubble.setObjectName("chatBubble")

        vBox = QVBoxLayout(bubble)
        vBox.setContentsMargins(14, 10, 14, 10)
        vBox.setSpacing(4)

        self.contentBubble = MarkdownBubble(self._content, self.is_user, bubble)
        timeLabel = CaptionLabel(self.timestamp.strftime("%H:%M"))
        timeLabel.setObjectName("chatTime")

        vBox.addWidget(self.contentBubble)
        vBox.addWidget(timeLabel)

        if self.is_user:
            bubble.setStyleSheet("""
                #chatBubble { background-color: #4A90D9; border: none; }
                #chatTime { color: rgba(255,255,255,160); }
            """)
            self.hBoxLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self.hBoxLayout.addWidget(bubble)
        else:
            bubble.setStyleSheet("""
                #chatBubble { background-color: #F5F5F5; border: none; }
                #chatTime { color: #999999; }
            """)
            self.hBoxLayout.addWidget(bubble)
            self.hBoxLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def update_content(self, content: str):
        self._content = content
        self.contentBubble.set_content(content, self.is_user)


class GatewayBar(QWidget):
    switch_character = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(52)
        self.setObjectName("gatewayBar")

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(12, 8, 12, 8)
        hbox.setSpacing(8)

        self.charCombo = QComboBox(self)
        self.charCombo.setFixedHeight(32)
        self.charCombo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.statusDot = QLabel("●", self)
        self.statusDot.setFixedSize(18, 18)
        self.statusDot.setAlignment(Qt.AlignCenter)
        self._set_status(False)

        self.portLabel = CaptionLabel("", self)
        self.portLabel.setFixedHeight(18)

        self.openBtn = QPushButton(self)
        self.openBtn.setIcon(FIF.GLOBE.icon())
        self.openBtn.setFixedSize(32, 32)
        self.openBtn.setToolTip("Open OpenClaw WebUI")

        hbox.addWidget(self.charCombo)
        hbox.addWidget(self.statusDot)
        hbox.addWidget(self.portLabel)
        hbox.addWidget(self.openBtn)

        self.setStyleSheet("""
            #gatewayBar { background: #F8F8F8; border-top: 1px solid #E0E0E0; border-radius: 0 0 12px 12px; }
        """)

        self.charCombo.currentTextChanged.connect(self._on_char_changed)
        self.openBtn.clicked.connect(self._open_webui)

    def populate_characters(self, pets: list, current: str):
        self.charCombo.blockSignals(True)
        self.charCombo.clear()
        for p in pets:
            self.charCombo.addItem(p)
        idx = self.charCombo.findText(current)
        if idx >= 0:
            self.charCombo.setCurrentIndex(idx)
        self.charCombo.blockSignals(False)
        self._update_port_label(current)

    def _on_char_changed(self, name: str):
        self._update_port_label(name)
        self.switch_character.emit(name)

    def _update_port_label(self, name: str):
        port = settings.openclaw_port_dict.get(name, 18789)
        self.portLabel.setText(f":{port}")

    def _set_status(self, running: bool):
        if running:
            self.statusDot.setStyleSheet("color: #2ECC71; font-size:14px;")
            self.statusDot.setToolTip("Gateway running")
        else:
            self.statusDot.setStyleSheet("color: #CCCCCC; font-size:14px;")
            self.statusDot.setToolTip("Gateway stopped")

    def set_gateway_running(self, running: bool):
        self._set_status(running)

    def _open_webui(self):
        current = self.charCombo.currentText()
        port = settings.openclaw_port_dict.get(current, 18789)
        QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:{port}"))


class ChatMessageList(QScrollArea):
    load_more_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        self.vBoxLayout.setContentsMargins(16, 16, 16, 16)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.addStretch()

        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setObjectName("chatMessageList")
        self.setStyleSheet("#chatMessageList { border: none; background-color: transparent; }")

        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._loading_more = False

    def add_message(self, sender: str, content: str, timestamp: datetime = None, prepend: bool = False):
        widget = ChatMessageWidget(sender, content, timestamp)
        if prepend:
            self.vBoxLayout.insertWidget(1, widget)
        else:
            self.vBoxLayout.insertWidget(self.vBoxLayout.count() - 1, widget)
            QTimer.singleShot(50, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))
        return widget

    def get_last_assistant_widget(self):
        for i in range(self.vBoxLayout.count() - 2, 0, -1):
            item = self.vBoxLayout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatMessageWidget):
                w = item.widget()
                if not w.is_user:
                    return w
        return None

    def clear_messages(self):
        while self.vBoxLayout.count() > 1:
            item = self.vBoxLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_scroll(self, value):
        if value == 0 and not self._loading_more:
            self._loading_more = True
            self.load_more_requested.emit()

    def done_loading_more(self):
        self._loading_more = False


class ChatInputPanel(QWidget):
    messageSubmitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(64)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(16, 10, 16, 10)
        hbox.setSpacing(12)

        self.inputEdit = QLineEdit(self)
        self.inputEdit.setPlaceholderText("Send a message...")
        self.inputEdit.setObjectName("chatInput")
        self.inputEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.inputEdit.setFixedHeight(44)

        self.sendButton = QPushButton(self)
        self.sendButton.setIcon(FIF.SEND.icon())
        self.sendButton.setObjectName("chatSendButton")
        self.sendButton.setFixedSize(44, 44)

        hbox.addWidget(self.inputEdit)
        hbox.addWidget(self.sendButton)

        self.setStyleSheet("""
            #chatInput { border: 1px solid #E0E0E0; border-radius: 22px; padding: 0 18px;
                         font-size: 14px; background-color: #FAFAFA; }
            #chatInput:focus { border: 2px solid #4A90D9; background-color: white; }
            #chatSendButton { background-color: #4A90D9; border-radius: 22px; border: none; }
            #chatSendButton:hover { background-color: #3A7BC8; }
            #chatSendButton:pressed { background-color: #2D6BB0; }
        """)

        self.sendButton.clicked.connect(self._on_send)
        self.inputEdit.returnPressed.connect(self._on_send)

    def _on_send(self):
        text = self.inputEdit.text().strip()
        if text:
            self.messageSubmitted.emit(text)
            self.inputEdit.clear()


class ChatCardGroup(QWidget):
    def __init__(self, title: str, sizeHintDyber, parent=None):
        super().__init__(parent=parent)
        self.sizeHintDyber = sizeHintDyber

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        self.messageList = ChatMessageList()
        self.inputPanel = ChatInputPanel()
        self.gatewayBar = GatewayBar()

        self.vBoxLayout.addWidget(self.messageList, 1)
        self.vBoxLayout.addWidget(self.inputPanel)
        self.vBoxLayout.addWidget(self.gatewayBar)

        self.inputPanel.messageSubmitted.connect(self._on_message_submitted)
        self.messageList.load_more_requested.connect(self._load_more_history)

        self._streaming_widget = None
        self._stream_timer = QTimer(self)
        self._stream_timer.setInterval(100)
        self._stream_timer.timeout.connect(self._flush_stream)
        self._pending_stream_content = None

        self._history_offset = 0
        self._history_page_size = 30

        self.setMinimumHeight(500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setObjectName("chatCardGroup")
        self.setStyleSheet("""
            #chatCardGroup { background-color: #FFFFFF; border-radius: 16px; border: 1px solid #E8E8E8; }
        """)

        self._init_openclaw_client()
        self._load_history()
        self._init_gateway_bar()

    def _init_gateway_bar(self):
        pets = getattr(settings, 'pets', [settings.petname]) if settings.petname else []
        if not pets:
            pets = [settings.petname]
        self.gatewayBar.populate_characters(pets, settings.petname)
        self.gatewayBar.switch_character.connect(self._on_gateway_char_changed)

        from DyberPet.OpenClawClient.gateway_manager import get_instance as get_gateway
        gm = get_gateway()
        gm.gateway_started.connect(lambda name, port: self.gatewayBar.set_gateway_running(True))
        gm.gateway_stopped.connect(lambda name: self.gatewayBar.set_gateway_running(False))
        self.gatewayBar.set_gateway_running(gm.is_running())

        if settings.openclaw_gateway_auto_start and settings.openclaw_token:
            port = settings.openclaw_port_dict.get(settings.petname, 18789)
            QTimer.singleShot(500, lambda: gm.switch_gateway(settings.petname, port, settings.openclaw_token))

    def _on_gateway_char_changed(self, name: str):
        from DyberPet.OpenClawClient.gateway_manager import get_instance as get_gateway
        port = settings.openclaw_port_dict.get(name, 18789)
        get_gateway().switch_gateway(name, port, settings.openclaw_token)

    def _load_history(self, prepend: bool = False):
        from DyberPet.OpenClawClient.chat_history import ChatHistoryManager
        mgr = ChatHistoryManager()
        msgs = mgr.load_history(settings.petname, limit=self._history_page_size, offset=self._history_offset)
        self._history_offset += len(msgs)
        for m in msgs:
            try:
                ts = datetime.fromisoformat(m.timestamp)
            except Exception:
                ts = None
            self.messageList.add_message(m.sender, m.content, ts, prepend=prepend)
        self.messageList.done_loading_more()

    def _load_more_history(self):
        self._load_history(prepend=True)

    def _init_openclaw_client(self):
        if settings.openclaw_enabled and settings.openclaw_token:
            from DyberPet.OpenClawClient import OpenClawWebSocketClient
            self._openclaw = OpenClawWebSocketClient(settings.openclaw_url, settings.openclaw_token)
            QTimer.singleShot(100, self._connect_openclaw_signals)
        else:
            self._openclaw = None

    def _connect_openclaw_signals(self):
        if self._openclaw:
            self._openclaw.message_received.connect(self._on_pet_message_received)
            self._openclaw.stream_delta.connect(self._on_stream_delta)
            self._openclaw.error_occurred.connect(self._on_openclaw_error)
            self._openclaw.start_connection()

    def _on_pet_message_received(self, content: str):
        self._stream_timer.stop()
        self._pending_stream_content = None
        if self._streaming_widget:
            self._streaming_widget.update_content(content)
            self._streaming_widget = None
        else:
            self.messageList.add_message("pet", content)
        self._save_message("pet", content)

    def _on_stream_delta(self, content: str):
        self._pending_stream_content = content
        if not self._stream_timer.isActive():
            self._stream_timer.start()
            if self._streaming_widget is None:
                self._streaming_widget = self.messageList.add_message("pet", content)

    def _flush_stream(self):
        if self._pending_stream_content is not None and self._streaming_widget is not None:
            self._streaming_widget.update_content(self._pending_stream_content)

    def _on_openclaw_error(self, error: str):
        self.messageList.add_message("pet", f"Connection error: {error}")

    def _on_message_submitted(self, text: str):
        self.messageList.add_message("user", text)
        self._save_message("user", text)
        if self._openclaw and self._openclaw.is_connected():
            self._openclaw.send_message(text)
        else:
            self.messageList.add_message("pet", "Chat is not connected. Please configure OpenClaw settings.")

    def _save_message(self, sender: str, content: str):
        from DyberPet.OpenClawClient.chat_history import ChatHistoryManager, ChatMessage as HistMsg
        import uuid
        mgr = ChatHistoryManager()
        msg = HistMsg(sender=sender, content=content,
                      timestamp=datetime.now().isoformat(),
                      id=str(uuid.uuid4()))
        mgr.save_message(settings.petname, msg)

    def on_pet_changed(self, new_pet_name: str = None):
        pet = new_pet_name or settings.petname
        self.messageList.clear_messages()
        self._history_offset = 0
        self._load_history()
        pets = getattr(settings, 'pets', [pet])
        self.gatewayBar.populate_characters(pets, pet)


class ChatInterface(QScrollArea):
    change_pet = Signal(str)

    def __init__(self, sizeHintDyber, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ChatInterface")
        self.sizeHintDyber = (sizeHintDyber[0] - 100, sizeHintDyber[1])

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.titleLabel = QLabel(self.tr("Chat with Pet"), self)
        self.titleLabel.setObjectName("chatTitle")

        self.__initCardLayout()
        self.__initWidget()

    def __initCardLayout(self):
        self.ChatCardGroup = ChatCardGroup(
            self.tr("Chat"), self.sizeHintDyber, self.scrollWidget)

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 60, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        self.__setQss()
        self.__initLayout()

    def __initLayout(self):
        self.expandLayout.setSpacing(20)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.ChatCardGroup)

    def __setQss(self):
        self.scrollWidget.setObjectName('scrollWidget')
        self.titleLabel.setObjectName('settingLabel')

        theme = 'light'
        qss_path = os.path.join(basedir, 'res/icons/system/qss', theme, 'setting_interface.qss')
        if os.path.isfile(qss_path):
            with open(qss_path, encoding='utf-8') as f:
                self.setStyleSheet(f.read())

    def on_pet_changed(self, new_pet_name: str = None):
        self.ChatCardGroup.on_pet_changed(new_pet_name)
