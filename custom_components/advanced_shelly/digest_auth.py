"""Digest authentication for aiohttp."""
import hashlib
import time
from typing import Optional
from aiohttp import ClientResponse


class DigestAuth:
    """HTTP Digest Authentication handler."""

    def __init__(self, username: str, password: str):
        """Initialize digest auth."""
        self.username = username
        self.password = password
        self.nc = 0
        self.last_challenge: Optional[dict] = None

    def _parse_challenge(self, auth_header: str) -> dict:
        """Parse WWW-Authenticate header."""
        challenge = {}
        parts = auth_header.replace("Digest ", "").split(", ")
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                challenge[key] = value.strip('"')
        return challenge

    def _build_digest_header(self, method: str, uri: str, challenge: dict) -> str:
        """Build Authorization header for digest auth."""
        realm = challenge.get("realm", "")
        nonce = challenge.get("nonce", "")
        qop = challenge.get("qop", "auth")
        algorithm = challenge.get("algorithm", "MD5")
        opaque = challenge.get("opaque", "")

        # Increment nonce count
        self.nc += 1
        nc_value = f"{self.nc:08x}"

        # Generate cnonce
        cnonce = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]

        # Calculate HA1
        ha1 = hashlib.md5(
            f"{self.username}:{realm}:{self.password}".encode()
        ).hexdigest()

        # Calculate HA2
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()

        # Calculate response
        if qop in ("auth", "auth-int"):
            response = hashlib.md5(
                f"{ha1}:{nonce}:{nc_value}:{cnonce}:{qop}:{ha2}".encode()
            ).hexdigest()
        else:
            response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()

        # Build header
        auth_header = (
            f'Digest username="{self.username}", '
            f'realm="{realm}", '
            f'nonce="{nonce}", '
            f'uri="{uri}", '
            f'algorithm={algorithm}, '
            f'response="{response}"'
        )

        if qop in ("auth", "auth-int"):
            auth_header += f', qop={qop}, nc={nc_value}, cnonce="{cnonce}"'

        if opaque:
            auth_header += f', opaque="{opaque}"'

        return auth_header

    def parse_and_save_challenge(self, response: ClientResponse) -> bool:
        """Parse and save challenge from 401 response."""
        if response.status != 401:
            return False

        auth_header = response.headers.get("WWW-Authenticate", "")
        if not auth_header.startswith("Digest "):
            return False

        self.last_challenge = self._parse_challenge(auth_header)
        return True

    def get_auth_header(self, method: str, url: str) -> Optional[str]:
        """Get Authorization header for a request."""
        if not self.last_challenge:
            return None

        # Extract path from URL
        from urllib.parse import urlparse
        uri = urlparse(url).path
        if urlparse(url).query:
            uri += "?" + urlparse(url).query

        return self._build_digest_header(method, uri, self.last_challenge)