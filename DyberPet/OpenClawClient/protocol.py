# coding:utf-8
import json
import uuid
import platform as platform_mod
from typing import Any, Dict, List, Optional

PROTOCOL_VERSION = 3
CLIENT_ID = "gateway-client"
CLIENT_VERSION = "1.0.0"
CLIENT_MODE = "backend"
ROLE = "operator"
SCOPES = ["operator.read", "operator.write"]


def _get_platform() -> str:
    system = platform_mod.system().lower()
    if system == "darwin":
        return "macos"
    return system


class ProtocolHandler:

    @staticmethod
    def build_connect_request(
        token: str,
        device_token: Optional[str] = None,
        device_field: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        platform_name = _get_platform()
        auth: Dict[str, Any] = {"token": token}
        if device_token:
            auth["deviceToken"] = device_token
        params: Dict[str, Any] = {
            "minProtocol": PROTOCOL_VERSION,
            "maxProtocol": PROTOCOL_VERSION,
            "client": {
                "id": CLIENT_ID,
                "version": CLIENT_VERSION,
                "platform": platform_name,
                "mode": CLIENT_MODE,
            },
            "role": ROLE,
            "scopes": SCOPES,
            "caps": [],
            "commands": [],
            "permissions": {},
            "auth": auth,
            "locale": "en-US",
            "userAgent": f"{CLIENT_ID}/{CLIENT_VERSION}",
        }
        if device_field:
            params["device"] = device_field
        return {
            "type": "req",
            "id": str(uuid.uuid4()),
            "method": "connect",
            "params": params,
        }

    @staticmethod
    def build_request(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "type": "req",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {},
        }

    @staticmethod
    def build_chat_send(content: str, session_key: str = "default") -> Dict[str, Any]:
        return ProtocolHandler.build_request("chat.send", {
            "sessionKey": session_key,
            "message": content,
            "idempotencyKey": str(uuid.uuid4()),
        })

    @staticmethod
    def parse_message(data: str) -> Dict[str, Any]:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse message: {e}")

    @staticmethod
    def is_connect_ok(message: Dict[str, Any]) -> bool:
        return (
            message.get("type") == "res"
            and message.get("ok") is True
            and message.get("payload", {}).get("type") == "hello-ok"
        )

    @staticmethod
    def is_connect_error(message: Dict[str, Any]) -> bool:
        return message.get("type") == "res" and message.get("ok") is False

    @staticmethod
    def is_response(message: Dict[str, Any]) -> bool:
        return message.get("type") == "res"

    @staticmethod
    def is_event(message: Dict[str, Any]) -> bool:
        return message.get("type") == "event"

    @staticmethod
    def is_challenge_event(message: Dict[str, Any]) -> bool:
        return (
            message.get("type") == "event"
            and message.get("event") == "connect.challenge"
        )

    @staticmethod
    def is_chat_event(message: Dict[str, Any]) -> bool:
        return (
            message.get("type") == "event"
            and message.get("event") == "chat"
        )

    @staticmethod
    def get_chat_event_state(message: Dict[str, Any]) -> Optional[str]:
        if ProtocolHandler.is_chat_event(message):
            return message.get("payload", {}).get("state")
        return None

    @staticmethod
    def extract_chat_content(message: Dict[str, Any]) -> Optional[str]:
        if not ProtocolHandler.is_chat_event(message):
            return None
        payload = message.get("payload", {})
        state = payload.get("state")
        if state == "error":
            return payload.get("errorMessage")
        if state in ("final", "delta"):
            msg = payload.get("message", {})
            content_list = msg.get("content", [])
            texts = []
            for block in content_list:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", ""))
            return "".join(texts) if texts else None
        return None
