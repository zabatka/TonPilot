from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from openai import AsyncOpenAI
from core.ton.indexer import get_wallet_jettons, get_ton_balance, get_recent_trades
from core.db.crud import get_user_wallet
from core.config import settings

router = Router()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
NL = ("pnl", "portfolio", "balance", "holdings", "how much", "worth", "rebalance")

@router.message(Command("portfolio"))
async def portfolio_cmd(message: Message):
    wallet = await get_user_wallet(message.from_user.id)
    if not wallet:
        return await message.answer("❌ No wallet connected.")
    ton = await get_ton_balance(wallet)
    jettons = await get_wallet_jettons(wallet)
    lines = [f"💎 TON: `{ton:.4f}`"]
    for item in jettons[:10]:
        sym = item["jetton"]["symbol"]
        bal = int(item["balance"]) / (10 ** item["jetton"].get("decimals", 9))
        lines.append(f"• {sym}: `{bal:.4f}`")
    await message.answer("📊 *Your TON Portfolio*\n\n" + "\n".join(lines))

@router.message(F.text.lower().func(lambda t: any(k in t for k in NL)))
async def nl_portfolio(message: Message):
    wallet = await get_user_wallet(message.from_user.id)
    if not wallet:
        return await message.answer("❌ No wallet connected.")
    ton = await get_ton_balance(wallet)
    trades = await get_recent_trades(wallet, 20)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content":
            f"User asks: '{message.text}'\nTON balance: {ton:.4f}, recent swaps: {len(trades)}\n"
            f"Answer in 2-3 sentences."}])
    await message.answer(f"📊 {resp.choices[0].message.content.strip()}")
