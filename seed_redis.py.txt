import redis.asyncio as redis
import asyncio

async def seed():
    r = redis.Redis(host='localhost', port=6379, db=0)
    await r.hset("trade:12345", mapping={
        "symbol": "EURUSD",
        "volume": "0.1",
        "override": ""
    })
    print("✅ Dummy trade seeded in Redis.")

asyncio.run(seed())
