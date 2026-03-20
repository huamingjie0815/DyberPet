# coding:utf-8
import os
import json
import time
import hashlib
import base64
from typing import Dict, List, Optional

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat, PrivateFormat, NoEncryption
    )
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def _base64url_decode(s: str) -> bytes:
    s += '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


class DeviceIdentity:

    def __init__(self, storage_path: str):
        self._storage_path = storage_path
        self._private_key = None
        self._public_key_raw: Optional[bytes] = None
        self._device_id: Optional[str] = None
        self._load_or_generate()

    def _load_or_generate(self):
        if not HAS_CRYPTO:
            raise ImportError(
                "cryptography package required for OpenClaw device auth: "
                "pip install cryptography"
            )
        if os.path.exists(self._storage_path):
            self._load()
        else:
            self._generate()

    def _load(self):
        with open(self._storage_path, 'r') as f:
            data = json.load(f)
        private_bytes = _base64url_decode(data['privateKey'])
        self._private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
        self._public_key_raw = self._private_key.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )
        self._device_id = hashlib.sha256(self._public_key_raw).hexdigest()
        self._device_token: Optional[str] = data.get('deviceToken')

    def _generate(self):
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key_raw = self._private_key.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )
        self._device_id = hashlib.sha256(self._public_key_raw).hexdigest()
        self._device_token: Optional[str] = None
        private_bytes = self._private_key.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption()
        )
        os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
        with open(self._storage_path, 'w') as f:
            json.dump({'privateKey': _base64url_encode(private_bytes)}, f)

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_token(self) -> Optional[str]:
        return self._device_token

    def save_device_token(self, token: str):
        self._device_token = token
        with open(self._storage_path, 'r') as f:
            data = json.load(f)
        data['deviceToken'] = token
        with open(self._storage_path, 'w') as f:
            json.dump(data, f)

    @property
    def public_key_b64url(self) -> str:
        return _base64url_encode(self._public_key_raw)

    def sign(self, payload: str) -> str:
        signature = self._private_key.sign(payload.encode('utf-8'))
        return _base64url_encode(signature)

    def build_connect_device_field(
        self,
        nonce: str,
        client_id: str,
        client_mode: str,
        role: str,
        scopes: List[str],
        token: str,
        platform_name: str,
        device_family: str,
    ) -> Dict:
        signed_at = int(time.time() * 1000)
        scopes_str = ",".join(scopes)
        payload = (
            f"v3|{self._device_id}|{client_id}|{client_mode}|{role}|{scopes_str}"
            f"|{signed_at}|{token}|{nonce}|{platform_name}|{device_family}"
        )
        signature = self.sign(payload)
        return {
            "id": self._device_id,
            "publicKey": self.public_key_b64url,
            "signature": signature,
            "signedAt": signed_at,
            "nonce": nonce,
        }
