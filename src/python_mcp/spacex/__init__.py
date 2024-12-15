import asyncio

from . import server


def run():
    print("Starting weather server (from run)...")
    asyncio.run(server.run())


__all__ = ["server"]
