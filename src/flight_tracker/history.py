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
    known = {(r["observed_on"], r["origin"], r["destination"], r["departure_date"], r["return_date"])
             for r in rows}
    for offer in offers:
        key = (observed_on, offer.origin, offer.destination, offer.departure_date, offer.return_date)
        if key in known:
            existing = next(r for r in rows if (r["observed_on"], r["origin"], r["destination"],
                r["departure_date"], r["return_date"]) == key)
            existing["price"] = min(float(existing["price"]), offer.price)
            if offer.booking_url:
                existing["booking_url"] = offer.booking_url
            if offer.airline_summary:
                existing["airline_summary"] = offer.airline_summary
            continue
        rows.append({
            "observed_on": observed_on,
            "origin": offer.origin,
            "destination": offer.destination,
            "departure_date": offer.departure_date,
            "return_date": offer.return_date,
            "price": offer.price,
            "currency": offer.currency,
            "booking_url": offer.booking_url,
            "airline_summary": offer.airline_summary,
        })
        known.add(key)
    rows.sort(key=lambda r: (r["observed_on"], r["destination"], r["price"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return rows


def cheapest_by_destination(rows: list[dict]) -> dict[str, dict]:
    cheapest: dict[str, dict] = {}
    for row in rows:
        current = cheapest.get(row["destination"])
        if current is None or float(row["price"]) < float(current["price"]):
            cheapest[row["destination"]] = row
    return cheapest
