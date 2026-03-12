from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from core.db.models import Base, User
from core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_user_wallet(telegram_id: int) -> str | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        return user.wallet_address if user else None


async def upsert_wallet(telegram_id: int, wallet_address: str):
    from datetime import datetime
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.wallet_address = wallet_address
            user.connected_at = datetime.utcnow()
        else:
            user = User(
                telegram_id=telegram_id,
                wallet_address=wallet_address,
                connected_at=datetime.utcnow(),
            )
            session.add(user)
        await session.commit()
