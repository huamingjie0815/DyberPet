# coding:utf-8
import socket
from typing import Optional, List

from PySide6.QtCore import QObject, QProcess, Signal


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def allocate_port(existing_ports: dict, base: int = 18789) -> int:
    used = set(existing_ports.values())
    port = base
    while port in used:
        port += 1
    return port


class GatewayProcessManager(QObject):
    """
    Manages the OpenClaw Gateway subprocess for the currently active character.
    Only one Gateway runs at a time (the active character's instance).
    """

    gateway_started = Signal(str, int)
    gateway_stopped = Signal(str)
    gateway_error = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._process: Optional[QProcess] = None
        self._active_character: Optional[str] = None
        self._active_port: Optional[int] = None

    @property
    def active_character(self) -> Optional[str]:
        return self._active_character

    @property
    def active_port(self) -> Optional[int]:
        return self._active_port

    def is_running(self) -> bool:
        return (
            self._process is not None
            and self._process.state() == QProcess.ProcessState.Running
        )

    def switch_gateway(self, character_name: str, port: int, token: str = "") -> bool:
        self.stop_gateway()
        return self.start_gateway(character_name, port, token)

    def start_gateway(self, character_name: str, port: int, token: str = "") -> bool:
        if self.is_running():
            self.stop_gateway()

        if is_port_in_use(port):
            self.gateway_error.emit(character_name, f"Port {port} is already in use")
            return False

        self._process = QProcess(self)
        cmd = self._build_command(character_name, port, token)
        self._process.setProgram(cmd[0])
        self._process.setArguments(cmd[1:])
        self._process.started.connect(lambda: self._on_started(character_name, port))
        self._process.finished.connect(lambda code, status: self._on_finished(character_name))
        self._process.errorOccurred.connect(lambda err: self._on_error(character_name))

        self._active_character = character_name
        self._active_port = port
        self._process.start()
        return True

    def stop_gateway(self) -> None:
        if self._process is None:
            return
        char = self._active_character
        self._process.terminate()
        if not self._process.waitForFinished(3000):
            self._process.kill()
        self._process = None
        self._active_character = None
        self._active_port = None
        if char:
            self.gateway_stopped.emit(char)

    def _build_command(self, character_name: str, port: int, token: str = "") -> List[str]:
        cmd = ["openclaw", "--profile", character_name, "gateway", "--port", str(port)]
        if token:
            cmd.extend(["--token", token])
        return cmd

    def _on_started(self, character_name: str, port: int) -> None:
        self.gateway_started.emit(character_name, port)

    def _on_finished(self, character_name: str) -> None:
        self._process = None
        self._active_character = None
        self._active_port = None
        self.gateway_stopped.emit(character_name)

    def _on_error(self, character_name: str) -> None:
        error_msg = self._process.errorString() if self._process else "Unknown error"
        self.gateway_error.emit(character_name, error_msg)


_instance: Optional[GatewayProcessManager] = None


def get_instance() -> GatewayProcessManager:
    global _instance
    if _instance is None:
        _instance = GatewayProcessManager()
    return _instance
