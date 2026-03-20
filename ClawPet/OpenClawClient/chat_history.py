# coding:utf-8
import os
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict

import ClawPet.settings as settings

HISTORY_DIR = os.path.join(settings.CONFIGDIR, "data", "chat_history")


@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: str = "text"

    @classmethod
    def from_dict(cls, d: dict) -> "ChatMessage":
        return cls(
            sender=d["sender"],
            content=d["content"],
            timestamp=d.get("timestamp", datetime.now().isoformat()),
            id=d.get("id", str(uuid.uuid4())),
            message_type=d.get("message_type", "text"),
        )

    def to_dict(self) -> dict:
        return asdict(self)


class ChatHistoryManager:
    """Manages per-character chat history stored in JSON files."""

    def _path(self, character: str) -> str:
        os.makedirs(HISTORY_DIR, exist_ok=True)
        return os.path.join(HISTORY_DIR, f"{character}.json")

    def _load_all(self, character: str) -> list[dict]:
        path = self._path(character)
        if not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("messages", [])
        except Exception:
            return []

    def _save_all(self, character: str, messages: list[dict]) -> None:
        path = self._path(character)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"messages": messages}, f, ensure_ascii=False, indent=2)

    def save_message(self, character: str, message: ChatMessage) -> None:
        messages = self._load_all(character)
        messages.append(message.to_dict())
        self._save_all(character, messages)

    def load_history(
        self, character: str, limit: int = 50, offset: int = 0
    ) -> list[ChatMessage]:
        all_msgs = self._load_all(character)
        total = len(all_msgs)
        start = max(0, total - limit - offset)
        end = total - offset if offset > 0 else total
        slice_ = all_msgs[start:end]
        return [ChatMessage.from_dict(m) for m in slice_]

    def clear_history(self, character: str) -> None:
        self._save_all(character, [])

    def count(self, character: str) -> int:
        return len(self._load_all(character))
