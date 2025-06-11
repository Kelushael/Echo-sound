import aiohttp
from solders.pubkey import Pubkey

SOL_DECIMALS = 1_000_000_000

async def check_funding(rpc_url: str, pubkey: Pubkey) -> float:
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json={"method": "getBalance", "params": [str(pubkey)]}) as resp:
            data = await resp.json()
            lamports = data.get("result", {}).get("value", 0)
            return lamports / SOL_DECIMALS
