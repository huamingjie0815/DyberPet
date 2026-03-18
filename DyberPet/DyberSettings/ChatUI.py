# coding:utf-8
import os
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit, QPushButton, QSizePolicy, QSpacerItem

from qfluentwidgets import FluentIcon as FIF, ExpandLayout
from qfluentwidgets import BodyLabel, CaptionLabel, setFont, CardWidget

import DyberPet.settings as settings
basedir = settings.BASEDIR


CHAT_MESSAGE_MAX_WIDTH = 320


class ChatMessage:
    """ Chat message data structure """

    def __init__(self, sender: str, content: str, timestamp: datetime = None):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp or datetime.now()


class ChatMessageWidget(QWidget):
    """ Single chat message display widget """

    def __init__(self, message: ChatMessage, parent=None):
        super().__init__(parent=parent)
        self.message = message
        self.is_user = message.sender == "user"

        self._init_ui()

    def _init_ui(self):
        self.setFixedWidth(CHAT_MESSAGE_MAX_WIDTH + 40)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(12, 8, 12, 8)
        self.hBoxLayout.setSpacing(8)

        if self.is_user:
            self.hBoxLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
            self._create_message_bubble(is_user=True)
        else:
            self._create_message_bubble(is_user=False)
            self.hBoxLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def _create_message_bubble(self, is_user: bool):
        bubble = CardWidget(self)
        bubble.setFixedWidth(CHAT_MESSAGE_MAX_WIDTH)
        bubble.setObjectName("chatBubble")

        vBox = QVBoxLayout(bubble)
        vBox.setContentsMargins(14, 10, 14, 10)
        vBox.setSpacing(4)

        contentLabel = BodyLabel(self.message.content)
        contentLabel.setWordWrap(True)
        contentLabel.setTextFormat(Qt.PlainText)

        timeLabel = CaptionLabel(self.message.timestamp.strftime("%H:%M"))
        timeLabel.setObjectName("chatTime")

        vBox.addWidget(contentLabel)
        vBox.addWidget(timeLabel)

        if is_user:
            bubble.setStyleSheet("""
                #chatBubble {
                    background-color: #4A90D9;
                    border: none;
                }
                #chatBubble BodyLabel {
                    color: white;
                }
                #chatTime {
                    color: rgba(255, 255, 255, 160);
                }
            """)
        else:
            bubble.setStyleSheet("""
                #chatBubble {
                    background-color: #F5F5F5;
                    border: none;
                }
                #chatBubble BodyLabel {
                    color: #333333;
                }
                #chatTime {
                    color: #999999;
                }
            """)

        self.hBoxLayout.addWidget(bubble)


class ChatMessageList(QScrollArea):
    """ Scrollable chat message list """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.messages = []

        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        self.vBoxLayout.setContentsMargins(16, 16, 16, 16)
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.addStretch()

        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setObjectName("chatMessageList")

        self.setStyleSheet("""
            #chatMessageList {
                border: none;
                background-color: transparent;
            }
        """)

    def add_message(self, message: ChatMessage):
        """ Add a new message to the list """
        msg_widget = ChatMessageWidget(message)
        self.vBoxLayout.insertWidget(self.vBoxLayout.count() - 1, msg_widget)
        self.messages.append(msg_widget)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """ Scroll to the bottom of the message list """
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))

    def clear(self):
        """ Clear all messages """
        while self.vBoxLayout.count() > 1:
            item = self.vBoxLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.messages.clear()


class ChatInputPanel(QWidget):
    """ Chat input panel with text field and send button """

    messageSubmitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._init_ui()

    def _init_ui(self):
        self.setFixedHeight(64)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(16, 10, 16, 10)
        self.hBoxLayout.setSpacing(12)

        self.inputEdit = QLineEdit(self)
        self.inputEdit.setPlaceholderText("Send a message...")
        self.inputEdit.setObjectName("chatInput")
        self.inputEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.inputEdit.setFixedHeight(44)

        self.sendButton = QPushButton(self)
        self.sendButton.setIcon(FIF.SEND.icon())
        self.sendButton.setObjectName("chatSendButton")
        self.sendButton.setFixedSize(44, 44)

        self.hBoxLayout.addWidget(self.inputEdit)
        self.hBoxLayout.addWidget(self.sendButton)

        self.setStyleSheet("""
            #chatInput {
                border: 1px solid #E0E0E0;
                border-radius: 22px;
                padding: 0 18px;
                font-size: 14px;
                background-color: #FAFAFA;
            }
            #chatInput:focus {
                border: 2px solid #4A90D9;
                background-color: white;
            }
            #chatSendButton {
                background-color: #4A90D9;
                border-radius: 22px;
                border: none;
            }
            #chatSendButton:hover {
                background-color: #3A7BC8;
            }
            #chatSendButton:pressed {
                background-color: #2D6BB0;
            }
        """)

        self.sendButton.clicked.connect(self._on_send_clicked)
        self.inputEdit.returnPressed.connect(self._on_send_clicked)

    def _on_send_clicked(self):
        text = self.inputEdit.text().strip()
        if text:
            self.messageSubmitted.emit(text)
            self.inputEdit.clear()

    def clear(self):
        """ Clear input text """
        self.inputEdit.clear()


class ChatCardGroup(QWidget):
    """ Chat card group widget containing message list and input panel """

    def __init__(self, title: str, sizeHintDyber, parent=None):
        super().__init__(parent=parent)
        self.sizeHintDyber = sizeHintDyber
        self.titleText = title

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.setSpacing(16)

        self.messageList = ChatMessageList()
        self.inputPanel = ChatInputPanel()

        self.vBoxLayout.addWidget(self.messageList, 1)
        self.vBoxLayout.addWidget(self.inputPanel)

        self.inputPanel.messageSubmitted.connect(self._on_message_submitted)

        self._streaming_widget = None
        self._init_openclaw_client()

        self.setMinimumHeight(500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setObjectName("chatCardGroup")
        self.setStyleSheet("""
            #chatCardGroup {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E8E8E8;
            }
        """)

    def _init_openclaw_client(self):
        """Initialize OpenClaw client if enabled"""
        from PySide6.QtCore import QTimer
        if settings.openclaw_enabled and settings.openclaw_token:
            from DyberPet.OpenClawClient import OpenClawWebSocketClient
            self._openclaw = OpenClawWebSocketClient(
                settings.openclaw_url,
                settings.openclaw_token
            )
            QTimer.singleShot(100, self._connect_openclaw_signals)
        else:
            self._openclaw = None

    def _connect_openclaw_signals(self):
        if self._openclaw:
            print("[ChatUI] Connecting OpenClaw signals...")
            self._openclaw.message_received.connect(self._on_pet_message_received)
            self._openclaw.stream_delta.connect(self._on_stream_delta)
            self._openclaw.error_occurred.connect(self._on_openclaw_error)
            self._openclaw.start_connection()
            print("[ChatUI] OpenClaw connection started")

    def _on_pet_message_received(self, content: str):
        print(f"[ChatUI] Received message: {content}")
        if self._streaming_widget:
            self._streaming_widget.deleteLater()
            self._streaming_widget = None
        pet_message = ChatMessage(sender="pet", content=content)
        self.messageList.add_message(pet_message)

    def _on_stream_delta(self, content: str):
        if self._streaming_widget is None:
            msg = ChatMessage(sender="pet", content=content)
            self._streaming_widget = ChatMessageWidget(msg)
            self.messageList.vBoxLayout.insertWidget(
                self.messageList.vBoxLayout.count() - 1,
                self._streaming_widget,
            )
            self.messageList._scroll_to_bottom()
        else:
            bubble = self._streaming_widget.findChild(CardWidget, "chatBubble")
            if bubble:
                label = bubble.findChild(BodyLabel)
                if label:
                    label.setText(content)
                    self.messageList._scroll_to_bottom()

    def _on_openclaw_error(self, error: str):
        """Handle OpenClaw error"""
        print(f"[ChatUI] Error: {error}")
        pet_message = ChatMessage(sender="pet", content=f"Connection error: {error}")
        self.messageList.add_message(pet_message)

    def adjustSize(self):
        """ Adjust widget size based on content """
        width = self.sizeHintDyber[0] - 50 if self.sizeHintDyber else 450
        return self.resize(width, self.minimumHeight())

    def _on_message_submitted(self, text: str):
        user_message = ChatMessage(sender="user", content=text)
        self.messageList.add_message(user_message)

        if self._openclaw and self._openclaw.is_connected():
            self._openclaw.send_message(text)
        else:
            pet_message = ChatMessage(sender="pet", content="Chat feature is under development. More features coming soon!")
            self.messageList.add_message(pet_message)

    def clear(self):
        """ Clear all messages """
        self.messageList.clear()


class ChatInterface(QScrollArea):
    """ Chat interface for pet conversation """

    def __init__(self, sizeHintDyber, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ChatInterface")
        self.sizeHintDyber = (sizeHintDyber[0]-100, sizeHintDyber[1])

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
        with open(os.path.join(basedir, 'res/icons/system/qss', theme, 'setting_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())
