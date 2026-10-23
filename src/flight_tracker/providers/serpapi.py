from datetime import date
import requests

from .base import FlightOffer


def _date_from_flight(flight: dict) -> str | None:
    value = (flight.get("departure_airport") or {}).get("date", "")
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return None


class SerpApiProvider:
    ENDPOINT = "https://serpapi.com/search.json"

    def __init__(self, api_key: str, country: str = "us", language: str = "en"):
        self.api_key = api_key
        self.country = country
        self.language = language

    def search(self, origin: str, destination: str, date_range_start: str,
               date_range_end: str, min_trip_length: int, max_trip_length: int,
               currency: str) -> list[FlightOffer]:
        params = {
            "engine": "google_flights",
            "api_key": self.api_key,
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": f"{date_range_start},{date_range_end}",
            "trip_length": f"{min_trip_length},{max_trip_length}",
            "currency": currency,
            "hl": self.language,
            "gl": self.country,
            "type": "1",
        }
        response = requests.get(self.ENDPOINT, params=params, timeout=90)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"SerpApi error for {origin}-{destination}: {payload['error']}")

        offers: list[FlightOffer] = []
        for group in ("best_flights", "other_flights"):
            for item in payload.get(group, []) or []:
                price = item.get("price")
                flights = item.get("flights", []) or []
                if price is None or not flights:
                    continue
                outbound_date = _date_from_flight(flights[0])
                return_date = _date_from_flight(flights[-1])
                if not outbound_date or not return_date:
                    continue
                trip_days = (date.fromisoformat(return_date) - date.fromisoformat(outbound_date)).days
                if trip_days < min_trip_length or trip_days > max_trip_length:
                    continue
                airlines = sorted({flight.get("airline", "") for flight in flights if flight.get("airline")})
                offers.append(FlightOffer(
                    origin=origin,
                    destination=destination,
                    departure_date=outbound_date,
                    return_date=return_date,
                    price=float(price),
                    currency=currency,
                    booking_url=item.get("link", ""),
                    airline_summary=", ".join(airlines),
                ))
        return offers
