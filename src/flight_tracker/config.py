import os
from dataclasses import dataclass


def _csv_env(name: str, default: str) -> tuple[str, ...]:
    return tuple(part.strip().upper() for part in os.getenv(name, default).split(",") if part.strip())


@dataclass(frozen=True)
class Config:
    origin: str
    destinations: tuple[str, ...]
    departure_date: str
    return_date: str
    currency: str
    country: str
    language: str
    min_alert_price: float | None
    max_alert_price: float | None
    serpapi_api_key: str
    discord_bot_token: str
    discord_channel_id: str
    discord_user_id: str

    @classmethod
    def from_env(cls) -> "Config":
        def optional_float(name: str) -> float | None:
            value = os.getenv(name, "").strip()
            return float(value) if value else None

        required = ("SERPAPI_API_KEY", "DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_ID", "DISCORD_USER_ID")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

        return cls(
            origin=os.getenv("ORIGIN_AIRPORT", "IAD").strip().upper(),
            destinations=_csv_env("DESTINATION_AIRPORTS", "TOS,KEF,ABZ,HEL"),
            departure_date=os.getenv("DEPARTURE_DATE", "2027-01-25"),
            return_date=os.getenv("RETURN_DATE", "2027-02-05"),
            currency=os.getenv("CURRENCY", "USD").strip().upper(),
            country=os.getenv("SERPAPI_COUNTRY", "us").strip().lower(),
            language=os.getenv("SERPAPI_LANGUAGE", "en").strip().lower(),
            min_alert_price=optional_float("MIN_ALERT_PRICE"),
            max_alert_price=optional_float("MAX_ALERT_PRICE"),
            serpapi_api_key=os.environ["SERPAPI_API_KEY"],
            discord_bot_token=os.environ["DISCORD_BOT_TOKEN"],
            discord_channel_id=os.environ["DISCORD_CHANNEL_ID"],
            discord_user_id=os.environ["DISCORD_USER_ID"],
        )
