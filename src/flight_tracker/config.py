import os
from dataclasses import dataclass


def _csv_env(name: str, default: str) -> tuple[str, ...]:
    return tuple(part.strip().upper() for part in os.getenv(name, default).split(",") if part.strip())


@dataclass(frozen=True)
class Config:
    origins: tuple[str, ...]
    destinations: tuple[str, ...]
    date_range_start: str
    date_range_end: str
    min_trip_length: int
    max_trip_length: int
    currency: str
    country: str
    language: str
    min_alert_price: float
    price_drop_alert: float
    serpapi_api_key: str
    discord_bot_token: str
    discord_channel_id_1: str
    discord_channel_id_2: str
    discord_user_id: str

    @classmethod
    def from_env(cls) -> "Config":
        required = (
            "SERPAPI_API_KEY", "DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_ID_1",
            "DISCORD_CHANNEL_ID_2", "DISCORD_USER_ID"
        )
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

        min_trip_length = int(os.getenv("MIN_TRIP_LENGTH", "3"))
        max_trip_length = int(os.getenv("MAX_TRIP_LENGTH", "11"))
        if min_trip_length < 1 or max_trip_length < min_trip_length:
            raise ValueError("Trip lengths must satisfy 1 <= MIN_TRIP_LENGTH <= MAX_TRIP_LENGTH")

        return cls(
            origins=_csv_env("ORIGIN_AIRPORTS", os.getenv("ORIGIN_AIRPORT", "IAD,RIC")),
            destinations=_csv_env("DESTINATION_AIRPORTS", "TOS,KEF,ABZ,HEL"),
            date_range_start=os.getenv("DATE_RANGE_START", os.getenv("DEPARTURE_DATE", "2027-01-25")),
            date_range_end=os.getenv("DATE_RANGE_END", os.getenv("RETURN_DATE", "2027-02-05")),
            min_trip_length=min_trip_length,
            max_trip_length=max_trip_length,
            currency=os.getenv("CURRENCY", "USD").strip().upper(),
            country=os.getenv("SERPAPI_COUNTRY", "us").strip().lower(),
            language=os.getenv("SERPAPI_LANGUAGE", "en").strip().lower(),
            min_alert_price=float(os.getenv("MIN_ALERT_PRICE", "500")),
            price_drop_alert=float(os.getenv("PRICE_DROP_ALERT", "50")),
            serpapi_api_key=os.environ["SERPAPI_API_KEY"],
            discord_bot_token=os.environ["DISCORD_BOT_TOKEN"],
            discord_channel_id_1=os.environ["DISCORD_CHANNEL_ID_1"],
            discord_channel_id_2=os.environ["DISCORD_CHANNEL_ID_2"],
            discord_user_id=os.environ["DISCORD_USER_ID"],
        )
