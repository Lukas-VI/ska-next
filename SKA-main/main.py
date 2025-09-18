import asyncio

from core.core import Core

if __name__ == "__main__":
    #langch server
    app = Core()
    asyncio.run(app.heart_beat())
