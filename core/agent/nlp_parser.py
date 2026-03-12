import json
from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel
from core.config import settings


class TradeIntent(BaseModel):
    action: str
    token_in: str
    token_out: str
    amount: float
    amount_type: str
    condition: Optional[str] = None
    slippage: float = 1.0


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a TON blockchain trading intent parser.
Extract the user's trade intent from natural language and return ONLY valid JSON.

Fields:
  action: "buy" | "sell" | "swap"
  token_in: source token symbol (what user is SPENDING)
  token_out: destination token symbol (what user RECEIVES)
  amount: numeric amount (float)
  amount_type: "exact" | "percentage"
  condition: optional trigger or null
  slippage: tolerance in percent, default 1.0

Known TON tokens: TON, USDT, NOT, STON, SCALE, DOGS, HMSTR

Examples:
  "buy 50 USDT of NOT"
  -> {"action":"buy","token_in":"USDT","token_out":"NOT","amount":50,"amount_type":"exact","condition":null,"slippage":1.0}

  "swap 20% of my TON to USDT when RSI drops below 30"
  -> {"action":"swap","token_in":"TON","token_out":"USDT","amount":20,"amount_type":"percentage","condition":"rsi_below_30","slippage":1.0}
"""


async def parse_trade_intent(user_message: str) -> TradeIntent:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(response.choices[0].message.content)
    return TradeIntent(**data)
