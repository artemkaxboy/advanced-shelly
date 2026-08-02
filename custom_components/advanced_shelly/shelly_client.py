import asyncio
import logging

from aiohttp import DigestAuthMiddleware, ClientSession, ClientTimeout

from .const import (
    SHELLY_USERNAME,
    DEFAULT_REQUEST_INTERVAL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF,
    MAX_BACKOFF,
)

_LOGGER = logging.getLogger(__name__)


class ShellyClient:
    def __init__(
            self,
            device_host: str,
            device_port: int,
            password: str | None,
            request_interval: float = DEFAULT_REQUEST_INTERVAL,
            max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.device_url = f"http://{device_host}:{int(device_port)}"
        self.middlewares = ()
        if password:
            digest_auth = DigestAuthMiddleware(login=SHELLY_USERNAME, password=password)
            self.middlewares = (digest_auth,)
        self.session = None
        self.request_interval = request_interval
        self.max_retries = max_retries
        self._lock = asyncio.Lock()
        self._next_request_at = 0.0

    async def __aenter__(self):

        self.session = ClientSession(middlewares=self.middlewares, timeout=ClientTimeout(total=10))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _throttle(self) -> None:
        """Keep at least `request_interval` seconds between RPC calls."""
        loop = asyncio.get_running_loop()
        wait = self._next_request_at - loop.time()
        if wait > 0:
            await asyncio.sleep(wait)
        self._next_request_at = loop.time() + self.request_interval

    @staticmethod
    def _retry_after(value: str | None) -> float | None:
        """Parse a Retry-After header holding a delay in seconds."""
        if not value:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            # HTTP-date form is not used by Shelly devices; fall back to backoff
            return None

    async def _request(self, method: str, path: str, **kwargs):
        """Perform a throttled RPC call, retrying when the device answers 429."""
        url = f"{self.device_url}{path}"
        backoff = DEFAULT_BACKOFF

        for attempt in range(self.max_retries + 1):
            async with self._lock:
                await self._throttle()
                async with self.session.request(method, url, **kwargs) as resp:
                    if resp.status != 429 or attempt == self.max_retries:
                        resp.raise_for_status()
                        return await resp.json()

                    delay = self._retry_after(resp.headers.get("Retry-After"))
                    if delay is None:
                        delay = backoff
                        backoff = min(backoff * 2, MAX_BACKOFF)
                    # Do not let the next call start before the backoff elapsed
                    self._next_request_at = asyncio.get_running_loop().time() + delay

            _LOGGER.debug(
                f"{url} rate limited (429), retrying in {delay:.1f}s "
                f"(attempt {attempt + 1}/{self.max_retries})"
            )
            await asyncio.sleep(delay)

    async def get_status(self):
        return await self._request('GET', '/rpc/Shelly.GetStatus')

    async def get_device_info(self):
        return await self._request('GET', '/rpc/Shelly.GetDeviceInfo')

    async def get_script_list(self):
        return await self._request('GET', '/rpc/Script.List')

    async def get_script_code(self, script_id: int):
        return await self._request('GET', '/rpc/Script.GetCode', params={'id': script_id})

    async def put_script_code(self, script_id: int, code: str):
        payload = {'id': script_id, 'code': code}
        return await self._request('POST', '/rpc/Script.PutCode', json=payload)

    async def get_config(self):
        """Get full device configuration."""
        return await self._request('GET', '/rpc/Shelly.GetConfig')

    async def set_config(self, config: dict):
        """Set device configuration."""
        return await self._request('POST', '/rpc/Shelly.SetConfig', json=config)
