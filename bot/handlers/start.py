from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

WELCOME_TEXT = """
⚡ *Welcome to TonPilot*

The first AI-native trading agent on TON, living inside Telegram.

*What I can do:*
• 🗣️ Trade with plain English: `buy 50 USDT of NOT`
• 📊 AI signals: `/signal NOT`
• 🐋 Whale copy-trade: `/whale`
• 💼 Portfolio check: `/portfolio`

Type anything to start, or use the commands above.
"""


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(WELCOME_TEXT)


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "*TonPilot Commands*\n\n"
        "/portfolio — View your token balances\n"
        "/signal <TOKEN> — AI on-chain signal (e.g. /signal NOT)\n"
        "/whale — Monitor whale wallets\n"
        "/help — Show this message\n\n"
        "*Just type naturally:*\n"
        "`buy 10 TON of NOT`\n"
        "`swap 25% of my USDT to TON`\n"
        "`what's my balance?`\n"
    )
    await message.answer(help_text)
