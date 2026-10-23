import json
from pathlib import Path
from typing import Iterable

from .providers.base import FlightOffer

HISTORY_PATH = Path("data/history.json")


def load_history(path: Path = HISTORY_PATH) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def record_offers(offers: Iterable[FlightOffer], observed_on: str,
                  path: Path = HISTORY_PATH) -> list[dict]:
    rows = load_history(path)
    for offer in offers:
        key = (observed_on, offer.origin, offer.destination)
        row = next((r for r in rows if (r["observed_on"], r["origin"], r["destination"]) == key), None)
        if row:
            if offer.price < float(row["price"]):
                row.update({"departure_date": offer.departure_date, "return_date": offer.return_date,
                            "price": offer.price, "currency": offer.currency,
                            "booking_url": offer.booking_url, "airline_summary": offer.airline_summary})
            continue
        rows.append({"observed_on": observed_on, "origin": offer.origin, "destination": offer.destination,
                     "departure_date": offer.departure_date, "return_date": offer.return_date,
                     "price": offer.price, "currency": offer.currency, "booking_url": offer.booking_url,
                     "airline_summary": offer.airline_summary})
    rows.sort(key=lambda r: (r["observed_on"], r["origin"], r["destination"], r["price"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


def previous_by_route(rows: list[dict], observed_on: str) -> dict[tuple[str, str], dict]:
    previous: dict[tuple[str, str], dict] = {}
    for row in rows:
        if row["observed_on"] >= observed_on:
            continue
        key = (row["origin"], row["destination"])
        if key not in previous or row["observed_on"] > previous[key]["observed_on"]:
            previous[key] = row
    return previous
