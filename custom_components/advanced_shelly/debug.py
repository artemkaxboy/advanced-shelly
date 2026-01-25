import asyncio

from shelly_client import ShellyClient


async def main():
    async with ShellyClient('http://192.168.0.10', 'password') as client:
        status = await client.get_status()
        print("Status:", status)

        device_info = await client.get_device_info()
        print("Device Info:", device_info)


if __name__ == '__main__':
    asyncio.run(main())
