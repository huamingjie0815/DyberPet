# coding:utf-8
import os
import time
import threading
import json
import websocket as ws_client
from PySide6.QtCore import QObject, Signal, QTimer

from .protocol import (
    ProtocolHandler, CLIENT_ID, CLIENT_MODE, ROLE, SCOPES, _get_platform,
)
from .exceptions import ConnectionError, HandshakeError

import DyberPet.settings as settings


class OpenClawWebSocketClient(QObject):

    connected = Signal()
    disconnected = Signal()
    message_received = Signal(str)
    stream_delta = Signal(str)
    error_occurred = Signal(str)
    connection_status_changed = Signal(bool)

    def __init__(self, url: str, token: str, parent=None):
        super().__init__(parent=parent)
        self.url = url
        self.token = token
        self.ws = None
        self._running = False
        self._connected = False
        self._reconnect = True
        self._reconnect_delay = 5
        self._session_key = "default"
        self._device_identity = None
        self._last_delta_text = ""
        self._pairing_pending = False
        self._init_device_identity()

    def _init_device_identity(self):
        try:
            from .device_identity import DeviceIdentity
            storage_path = os.path.join(
                settings.BASEDIR, "data", "openclaw_device.json"
            )
            self._device_identity = DeviceIdentity(storage_path)
        except ImportError as e:
            print(f"[OpenClaw] Device identity unavailable: {e}")
            self._device_identity = None

    def _on_open(self, ws):
        print("[OpenClaw] Connection opened, waiting for challenge...")

    def _on_message(self, ws, message):
        try:
            msg = ProtocolHandler.parse_message(message)
            msg_type = msg.get("type")

            if msg_type == "event" and ProtocolHandler.is_challenge_event(msg):
                self._handle_challenge(ws, msg)
            elif msg_type == "res":
                self._handle_response(ws, msg)
            elif msg_type == "event" and ProtocolHandler.is_chat_event(msg):
                self._handle_chat_event(msg)
        except Exception as e:
            self.error_occurred.emit(f"Message parse error: {str(e)}")

    def _handle_challenge(self, ws, msg):
        payload = msg.get("payload", {})
        nonce = payload.get("nonce", "")
        device_field = None
        if self._device_identity:
            device_field = self._device_identity.build_connect_device_field(
                nonce=nonce,
                client_id=CLIENT_ID,
                client_mode=CLIENT_MODE,
                role=ROLE,
                scopes=SCOPES,
                token=self.token,
                platform_name=_get_platform(),
                device_family="",
            )
        connect_req = ProtocolHandler.build_connect_request(
            token=self.token,
            device_token=self._device_identity.device_token if self._device_identity else None,
            device_field=device_field,
        )
        ws.send(json.dumps(connect_req))

    def _handle_response(self, ws, msg):
        if ProtocolHandler.is_connect_ok(msg):
            self._connected = True
            self.connection_status_changed.emit(True)
            self.connected.emit()
            payload = msg.get("payload", {})
            policy = payload.get("policy", {})
            device_token = payload.get("auth", {}).get("deviceToken")
            if device_token and self._device_identity:
                self._device_identity.save_device_token(device_token)
                print(f"[OpenClaw] Device token saved.")
            print(f"[OpenClaw] Connected. Policy: {policy}")
        elif ProtocolHandler.is_connect_error(msg):
            error = msg.get("error", {})
            error_msg = error.get("message", "Unknown error") if isinstance(error, dict) else str(error)
            details = error.get("details", {}) if isinstance(error, dict) else {}
            detail_code = details.get("code", "") if isinstance(details, dict) else ""

            if detail_code == "PAIRING_REQUIRED":
                request_id = details.get("requestId", "")
                print(f"[OpenClaw] Pairing required (requestId={request_id}), will retry after approval...")
                self._pairing_pending = True
            else:
                self.error_occurred.emit(f"Handshake failed: {error_msg}")
                self._reconnect = False
                ws.close()

    def _handle_chat_event(self, msg):
        state = ProtocolHandler.get_chat_event_state(msg)
        content = ProtocolHandler.extract_chat_content(msg)
        if state == "delta" and content is not None:
            self._last_delta_text = content
            self.stream_delta.emit(content)
        elif state == "final" and content is not None:
            self._last_delta_text = ""
            self.message_received.emit(content)
        elif state == "error" and content is not None:
            self.error_occurred.emit(f"Chat error: {content}")
            self._last_delta_text = ""

    def _on_error(self, ws, error):
        print(f"[OpenClaw] Error: {error}")
        self.error_occurred.emit(f"WebSocket error: {str(error)}")

    def _on_close(self, ws, close_status_code, close_msg):
        print(f"[OpenClaw] Connection closed: {close_status_code} - {close_msg}")
        self._connected = False
        self.disconnected.emit()
        self.connection_status_changed.emit(False)
        if self._reconnect and self._running:
            delay = 2 if self._pairing_pending else self._reconnect_delay
            self._pairing_pending = False
            print(f"[OpenClaw] Reconnecting in {delay}s...")
            time.sleep(delay)
            if self._running and self._reconnect:
                self._start_ws()

    def _start_ws(self):
        self.ws = ws_client.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.ws.run_forever(ping_interval=30)

    def _run_websocket(self):
        self._running = True
        self._start_ws()

    def start_connection(self):
        self._reconnect = True
        thread = threading.Thread(target=self._run_websocket, daemon=True)
        thread.start()

    def stop_connection(self):
        self._reconnect = False
        self._running = False
        if self.ws:
            self.ws.close()

    def send_message(self, content: str) -> bool:
        if not self._connected or not self.ws:
            self.error_occurred.emit("Not connected to gateway")
            return False
        try:
            chat_req = ProtocolHandler.build_chat_send(content, self._session_key)
            self.ws.send(json.dumps(chat_req))
            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to send message: {str(e)}")
            return False

    def is_connected(self) -> bool:
        return self._connected
