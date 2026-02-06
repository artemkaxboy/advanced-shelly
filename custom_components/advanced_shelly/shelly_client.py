from aiohttp import DigestAuthMiddleware, ClientSession, ClientTimeout

from .const import SHELLY_USERNAME


class ShellyClient:
    def __init__(self, device_host: str, device_port: int, password: str):
        self.device_url = f"http://{device_host}:{int(device_port)}"
        self.middlewares = ()
        if password:
            digest_auth = DigestAuthMiddleware(login=SHELLY_USERNAME, password=password)
            self.middlewares = (digest_auth,)
        self.session = None

    async def __aenter__(self):

        self.session = ClientSession(middlewares=self.middlewares, timeout=ClientTimeout(total=10))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_status(self):
        async with self.session.get(f'{self.device_url}/rpc/Shelly.GetStatus') as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_device_info(self):
        async with self.session.get(f'{self.device_url}/rpc/Shelly.GetDeviceInfo') as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_script_list(self):
        async with self.session.get(f'{self.device_url}/rpc/Script.List') as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_script_code(self, script_id: int):
        async with self.session.get(f'{self.device_url}/rpc/Script.GetCode', params={'id': script_id}) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def put_script_code(self, script_id: int, code: str):
        payload = {'id': script_id, 'code': code}
        async with self.session.post(f'{self.device_url}/rpc/Script.PutCode', json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_config(self):
        """Get full device configuration."""
        async with self.session.get(f'{self.device_url}/rpc/Shelly.GetConfig') as resp:
            resp.raise_for_status()
            return await resp.json()

    async def set_config(self, config: dict):
        """Set device configuration."""
        async with self.session.post(f'{self.device_url}/rpc/Shelly.SetConfig', json=config) as resp:
            resp.raise_for_status()
            return await resp.json()