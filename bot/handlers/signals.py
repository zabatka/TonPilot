from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.agent.signal_engine import fetch_jetton_metrics, generate_signal
from core.ton.dex import JETTON_ADDRESSES

router = Router()


@router.message(Command("signal"))
async def signal_cmd(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer(
            "Usage: `/signal TOKEN`\nExample: `/signal NOT`\n\n"
            f"Available: {', '.join(JETTON_ADDRESSES.keys())}"
        )

    token = parts[1].upper()
    address = JETTON_ADDRESSES.get(token)
    if not address:
        return await message.answer(
            f"❌ Unknown token `{token}`.\nAvailable: {', '.join(JETTON_ADDRESSES.keys())}"
        )

    thinking = await message.answer(f"🔍 Analyzing on-chain data for *{token}*...")
    try:
        metrics = await fetch_jetton_metrics(address)
        signal = await generate_signal(token, metrics)
        text = (
            f"📡 *AI Signal — {token}*\n\n"
            f"{signal}\n\n"
            f"_Holders: {metrics['holders_count']:,} | "
            f"Top-50 concentration: {metrics['top50_concentration_pct']}%_"
        )
        await thinking.edit_text(text)
    except Exception as e:
        await thinking.edit_text(f"❌ Signal failed: {e}")
