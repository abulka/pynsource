import asyncio
import aiohttp
from async_lru import alru_cache

@alru_cache(maxsize=32)
async def url_to_data(url):

    # await asyncio.sleep(5)

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            return await response.read(), response.status
