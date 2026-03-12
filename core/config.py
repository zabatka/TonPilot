from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    OPENAI_API_KEY: str
    TONAPI_KEY: str
    STONFI_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./tonpilot.db"
    TONPILOT_REFERRAL_WALLET: str = ""
    WHALE_WALLETS: str = ""
    AGENT_API_SECRET: str = ""

    @property
    def whale_wallet_list(self) -> list[str]:
        return [w.strip() for w in self.WHALE_WALLETS.split(",") if w.strip()]


settings = Settings()
