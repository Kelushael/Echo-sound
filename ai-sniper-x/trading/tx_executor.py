import aiohttp
from solders.rpc.config import RpcSendTransactionConfig

async def send_transaction(rpc_url: str, tx: str) -> str:
    payload = {
        "method": "sendTransaction",
        "params": [tx, RpcSendTransactionConfig(skip_preflight=True, preflight_commitment='confirmed').to_json()]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as resp:
            data = await resp.json()
            return data.get("result", "")
