"""define the normalized offer model and provider contract."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FlightOffer:
    """hold the route, dates, price, and booking details for one offer."""

    origin: str
    destination: str
    departure_date: str
    return_date: str
    price: float
    currency: str
    booking_url: str = ""
    airline_summary: str = ""


class FlightProvider(Protocol):
    """define the search method required of each provider adapter."""

    def search(self, origin: str, destination: str, departure_date: str,
               return_date: str, currency: str) -> list[FlightOffer]:
        """return normalized round-trip offers for a route and date pair."""
