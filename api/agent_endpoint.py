from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from core.config import settings
from core.ton.dex import get_swap_quote, build_swap_tx

app = FastAPI(title="TonPilot Agent API", version="1.0.0")


class TradeRequest(BaseModel):
    wallet_address: str
    token_in: str
    token_out: str
    amount: float
    slippage: float = 1.0


class TradeResponse(BaseModel):
    status: str
    quote_ask_units: int
    boc: str


@app.post("/v1/trade", response_model=TradeResponse)
async def agent_trade(
    req: TradeRequest,
    x_api_secret: str = Header(..., alias="X-Api-Secret"),
):
    if x_api_secret != settings.AGENT_API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API secret")

    amount_in = int(req.amount * 1e9)
    try:
        quote = await get_swap_quote(req.token_in, req.token_out, amount_in, req.slippage)
        ask_units = int(quote["ask_units"])
        min_out = int(ask_units * (1 - req.slippage / 100))
        boc = await build_swap_tx(
            req.wallet_address, req.token_in, req.token_out, amount_in, min_out
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return TradeResponse(status="ok", quote_ask_units=ask_units, boc=boc)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "TonPilot Agent API"}
