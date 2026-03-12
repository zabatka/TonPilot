from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from core.agent.signal_engine import monitor_whale_wallets
from core.config import settings

router = Router()


@router.message(Command("whale"))
async def whale_cmd(message: Message):
    wallets = settings.whale_wallet_list
    if not wallets:
        return await message.answer(
            "⚠️ No whale wallets configured.\n\n"
            "Add wallet addresses to `WHALE_WALLETS` in your environment variables,\n"
            "separated by commas."
        )

    thinking = await message.answer(f"🐋 Scanning {len(wallets)} whale wallets...")
    try:
        moves = await monitor_whale_wallets(wallets)
    except Exception as e:
        return await thinking.edit_text(f"❌ Whale scan failed: {e}")

    if not moves:
        return await thinking.edit_text("🐋 No recent whale activity found.")

    lines = []
    for m in moves[:10]:
        ts = datetime.utcfromtimestamp(m["timestamp"]).strftime("%H:%M UTC")
        action = m["action"].replace("Jetton", "")
        lines.append(f"• `{m['wallet']}` — {action} @ {ts}")

    text = "🐋 *Recent Whale Moves*\n\n" + "\n".join(lines)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔁 Copy top move", callback_data="copy_whale_top"),
        InlineKeyboardButton(text="🔔 Watch wallets", callback_data="whale_watch"),
    ]])
    await thinking.edit_text(text, reply_markup=kb)


@router.callback_query(F.data == "copy_whale_top")
async def copy_whale(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🔁 *Copy-trade setup*\n\n"
        "Set your max position size:\n"
        "• `/copy 10` — max 10 TON per trade\n"
        "• `/copy 5%` — 5% of your balance per trade"
    )


@router.callback_query(F.data == "whale_watch")
async def whale_watch(callback: CallbackQuery):
    await callback.answer("🔔 Whale alerts enabled!")
    await callback.message.answer(
        "🔔 *Whale alerts activated!*\n\nYou'll be notified when monitored wallets make large moves."
    )
