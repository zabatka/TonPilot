from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    wallet_address = Column(String, nullable=True)
    connected_at = Column(DateTime, nullable=True)
    whale_watch_enabled = Column(Boolean, default=False)
    copy_trade_max_ton = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    token_in = Column(String, nullable=False)
    token_out = Column(String, nullable=False)
    amount_in = Column(Float, nullable=False)
    amount_out = Column(Float, nullable=True)
    tx_hash = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
