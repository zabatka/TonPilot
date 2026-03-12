import aiohttp
from core.config import settings

STONFI_API_BASE = "https://api.ston.fi/v1"

JETTON_ADDRESSES: dict[str, str] = {
    "USDT":  "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs",
    "NOT":   "EQAvlWFDxGF2lXm67y4yzC17wYKD9A0guwPkMs1gOsM__NOT",
    "STON":  "EQA2kCVNwVsil2EM2mB0sPeeRqNqHnYeqkAwhZcNebWOb6bH",
    "SCALE": "EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE",
    "DOGS":  "EQCvxJy4eG8hyHBFsZ7eePxrRsUQSFE_jpptRAYBmcG_DOGS",
    "HMSTR": "EQAJ8uWd7EBqsmpSWaRdf_I-8R8-XHwh3gsNKhy-UrdrHMSTR",
}
TON_PROXY = "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"


def resolve_address(token: str) -> str:
    if token.upper() == "TON":
        return TON_PROXY
    addr = JETTON_ADDRESSES.get(token.upper())
    if not addr:
        raise ValueError(f"Unknown token: {token}")
    return addr


async def get_swap_quote(
    token_in: str, token_out: str, amount_in: int, slippage: float = 1.0
) -> dict:
    params = {
        "offer_address": resolve_address(token_in),
        "ask_address": resolve_address(token_out),
        "offer_units": str(amount_in),
        "slippage_tolerance": str(slippage / 100),
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{STONFI_API_BASE}/swap/simulate", params=params
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


async def build_swap_tx(
    user_wallet: str,
    token_in: str,
    token_out: str,
    amount_in: int,
    min_out: int,
) -> str:
    payload = {
        "user_wallet_address": user_wallet,
        "offer_jetton_address": resolve_address(token_in),
        "ask_jetton_address": resolve_address(token_out),
        "offer_amount": str(amount_in),
        "min_ask_amount": str(min_out),
        "referral_address": settings.TONPILOT_REFERRAL_WALLET or None,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{STONFI_API_BASE}/swap/build", json=payload
        ) as resp:
            resp.raise_for_status()
            result = await resp.json()
            return result["transaction"]
