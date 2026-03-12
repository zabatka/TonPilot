from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from core.agent.nlp_parser import parse_trade_intent, TradeIntent
from core.ton.dex import get_swap_quote, build_swap_tx
from core.db.crud import get_user_wallet

router = Router()

TRADE_KEYWORDS = ("buy", "sell", "swap", "trade", "exchange", "convert", "get me")
TOKEN_DECIMALS = {
    "TON": 9, "USDT": 6, "NOT": 9,
    "STON": 9, "SCALE": 9, "DOGS": 9, "HMSTR": 9,
}


def _is_trade_message(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in TRADE_KEYWORDS)


@router.message(F.text.func(_is_trade_message))
async def handle_trade(message: Message, state: FSMContext):
    wallet = await get_user_wallet(message.from_user.id)
    if not wallet:
        return await message.answer(
            "❌ No wallet connected.\n\nFor this demo, use wallet address:\n"
            "`EQDemo_wallet_address_here`\n\n"
            "In production, use /connect to link Tonkeeper."
        )

    thinking = await message.answer("🤖 Parsing trade intent...")

    try:
        intent: TradeIntent = await parse_trade_intent(message.text)
    except Exception as e:
        return await thinking.edit_text(f"❌ Could not parse intent: {e}")

    decimals_in = TOKEN_DECIMALS.get(intent.token_in.upper(), 9)
    amount_in = int(intent.amount * (10 ** decimals_in))

    try:
        quote = await get_swap_quote(
            intent.token_in, intent.token_out, amount_in, intent.slippage
        )
    except Exception as e:
        return await thinking.edit_text(f"❌ DEX quote failed: {e}")

    ask_units = int(quote.get("ask_units", 0))
    decimals_out = TOKEN_DECIMALS.get(intent.token_out.upper(), 9)
    amount_out_human = ask_units / (10 ** decimals_out)
    min_out = int(ask_units * (1 - intent.slippage / 100))

    condition_line = f"⏳ Trigger: `{intent.condition}`\n" if intent.condition else ""
    text = (
        f"🔄 *Trade Preview*\n\n"
        f"🔵 Spend:   `{intent.amount} {intent.token_in.upper()}`\n"
        f"🟢 Receive: `{amount_out_human:.4f} {intent.token_out.upper()}` (est.)\n"
        f"📉 Slippage: `{intent.slippage}%`\n"
        f"{condition_line}"
        f"\nConfirm?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Confirm",
            callback_data=f"ct|{intent.token_in}|{intent.token_out}|{amount_in}|{min_out}",
        ),
        InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_trade"),
    ]])
    await thinking.edit_text(text, reply_markup=kb)
    await state.update_data(pending_trade=intent.model_dump())


@router.callback_query(F.data.startswith("ct|"))
async def confirm_trade(callback: CallbackQuery, state: FSMContext):
    _, token_in, token_out, amount_in, min_out = callback.data.split("|")
    wallet = await get_user_wallet(callback.from_user.id)
    await callback.answer()
    await callback.message.edit_text("⏳ Building transaction...")
    try:
        boc = await build_swap_tx(
            wallet, token_in, token_out, int(amount_in), int(min_out)
        )
        deeplink = f"https://app.tonkeeper.com/transfer?boc={boc}"
        await callback.message.edit_text(
            f"✅ *Transaction ready!*\n\n[👆 Sign in Tonkeeper]({deeplink})",
        )
    except Exception as e:
        await callback.message.edit_text(f"❌ Transaction build failed: {e}")
    await state.clear()


@router.callback_query(F.data == "cancel_trade")
async def cancel_trade(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Cancelled")
    await callback.message.edit_text("❌ Trade cancelled.")
    await state.clear()
