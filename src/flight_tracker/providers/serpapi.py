from datetime import date
import requests

from .base import FlightOffer


DESTINATION_QUERIES = {
    "TOS": "Tromso Norway",
    "KEF": "Keflavik Iceland",
    "ABZ": "Aberdeen Scotland",
    "HEL": "Helsinki Finland",
    "ALF": "Alta Norway",
    "BOO": "Bodo Norway",
    "EVE": "Evenes Norway",
    "KKN": "Kirkenes Norway",
    "LYR": "Longyearbyen Svalbard",
    "KTT": "Kittila Finland",
    "RVN": "Rovaniemi Finland",
    "IVL": "Ivalo Finland",
    "KRN": "Kiruna Sweden",
    "LLA": "Lulea Sweden",
    "SFJ": "Kangerlussuaq Greenland",
    "GOH": "Nuuk Greenland",
    "YXY": "Whitehorse Canada",
    "YZF": "Yellowknife Canada",
    "FAI": "Fairbanks Alaska",
}


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
            "engine": "google_flights_deals",
            "api_key": self.api_key,
            "departure_id": origin,
            "query": DESTINATION_QUERIES.get(destination, destination),
            "outbound_date": f"{date_range_start},{date_range_end}",
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
        for item in payload.get("deals", []) or []:
            price = item.get("price")
            outbound_date = item.get("start_date")
            return_date = item.get("end_date")
            arrival_code = item.get("arrival_airport_code", "")
            if price is None or not outbound_date or not return_date:
                continue
            if arrival_code and arrival_code.upper() != destination:
                continue
            try:
                trip_days = (date.fromisoformat(return_date) - date.fromisoformat(outbound_date)).days
            except ValueError:
                continue
            if trip_days < min_trip_length or trip_days > max_trip_length:
                continue
            offers.append(FlightOffer(
                origin=origin,
                destination=destination,
                departure_date=outbound_date,
                return_date=return_date,
                price=float(price),
                currency=currency,
                booking_url=item.get("flight_link", ""),
                airline_summary=item.get("airline", ""),
            ))
        return offers
