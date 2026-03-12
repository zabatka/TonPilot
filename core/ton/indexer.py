import aiohttp
from core.config import settings

TONAPI_BASE = "https://tonapi.io/v2"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.TONAPI_KEY}"}


async def get_wallet_jettons(wallet_address: str) -> list[dict]:
    async with aiohttp.ClientSession(headers=_headers()) as s:
        async with s.get(f"{TONAPI_BASE}/accounts/{wallet_address}/jettons") as r:
            r.raise_for_status()
            data = await r.json()
    return data.get("balances", [])


async def get_ton_balance(wallet_address: str) -> float:
    async with aiohttp.ClientSession(headers=_headers()) as s:
        async with s.get(f"{TONAPI_BASE}/accounts/{wallet_address}") as r:
            r.raise_for_status()
            data = await r.json()
    return int(data.get("balance", 0)) / 1e9


async def get_recent_trades(wallet_address: str, limit: int = 20) -> list[dict]:
    async with aiohttp.ClientSession(headers=_headers()) as s:
        async with s.get(
            f"{TONAPI_BASE}/accounts/{wallet_address}/events",
            params={"limit": limit, "subject_only": "true"},
        ) as r:
            r.raise_for_status()
            data = await r.json()
    trades = []
    for event in data.get("events", []):
        for action in event.get("actions", []):
            if action.get("type") == "JettonSwap":
                trades.append({
                    "timestamp": event["timestamp"],
                    "token_in": action.get("jettonMasterIn", {}).get("symbol"),
                    "token_out": action.get("jettonMasterOut", {}).get("symbol"),
                    "amount_in": action.get("amountIn"),
                    "amount_out": action.get("amountOut"),
                })
    return trades
