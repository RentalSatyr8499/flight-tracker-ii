from datetime import date
import requests

from .base import FlightOffer


class SerpApiProvider:
    ENDPOINT = "https://serpapi.com/search.json"

    def __init__(self, api_key: str, country: str = "us", language: str = "en"):
        self.api_key = api_key
        self.country = country
        self.language = language

    def search(self, origin: str, destination: str, departure_date: str,
               return_date: str, currency: str) -> list[FlightOffer]:
        params = {
            "engine": "google_flights",
            "api_key": self.api_key,
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "return_date": return_date,
            "currency": currency,
            "hl": self.language,
            "gl": self.country,
            "type": "1",
        }
        response = requests.get(self.ENDPOINT, params=params, timeout=45)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"SerpApi error for {origin}-{destination}: {payload['error']}")

        offers: list[FlightOffer] = []
        for group in ("best_flights", "other_flights"):
            for item in payload.get(group, []) or []:
                price = item.get("price")
                if price is None:
                    continue
                flights = item.get("flights", []) or []
                airlines = sorted({flight.get("airline", "") for flight in flights if flight.get("airline")})
                offers.append(FlightOffer(
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    return_date=return_date,
                    price=float(price),
                    currency=currency,
                    booking_url=item.get("link", ""),
                    airline_summary=", ".join(airlines),
                ))
        return offers
