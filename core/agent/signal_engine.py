import aiohttp
from openai import AsyncOpenAI
from core.config import settings

TONAPI_BASE = "https://tonapi.io/v2"
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def fetch_jetton_metrics(token_address: str) -> dict:
    headers = {"Authorization": f"Bearer {settings.TONAPI_KEY}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"{TONAPI_BASE}/jettons/{token_address}") as r:
            info = await r.json()
        async with session.get(
            f"{TONAPI_BASE}/jettons/{token_address}/holders",
            params={"limit": 50},
        ) as r:
            holders_resp = await r.json()

    holders = holders_resp.get("addresses", [])
    total_supply = int(info.get("total_supply", 1) or 1)
    top50_balance = sum(int(h.get("balance", 0)) for h in holders)
    concentration = round(top50_balance / total_supply * 100, 2) if total_supply else 0

    return {
        "symbol": info.get("metadata", {}).get("symbol", "UNKNOWN"),
        "total_supply": total_supply,
        "holders_count": info.get("holders_count", 0),
        "top50_concentration_pct": concentration,
    }


async def generate_signal(token: str, metrics: dict) -> str:
    prompt = (
        f"You are a TON blockchain trading analyst.\n"
        f"Token: {metrics['symbol']}\n"
        f"Total Supply: {metrics['total_supply']:,}\n"
        f"Total Holders: {metrics['holders_count']:,}\n"
        f"Top-50 Holder Concentration: {metrics['top50_concentration_pct']}%\n\n"
        f"Output a single line: [BULLISH/BEARISH/NEUTRAL] followed by 2 sentences of reasoning."
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


async def monitor_whale_wallets(addresses: list[str]) -> list[dict]:
    moves = []
    headers = {"Authorization": f"Bearer {settings.TONAPI_KEY}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        for addr in addresses:
            async with session.get(
                f"{TONAPI_BASE}/accounts/{addr}/events",
                params={"limit": 10, "subject_only": "true"},
            ) as r:
                data = await r.json()
            for event in data.get("events", []):
                for action in event.get("actions", []):
                    if action.get("type") in ("JettonSwap", "JettonTransfer"):
                        moves.append({
                            "wallet": addr[:8] + "...",
                            "action": action["type"],
                            "timestamp": event["timestamp"],
                            "details": action,
                        })
    return moves
