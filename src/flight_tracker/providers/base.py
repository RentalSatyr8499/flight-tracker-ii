"""define the normalized offer model and provider contract."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FlightOffer:
    """hold the route, selected travel dates, price, and booking details."""

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

    def search(self, origin: str, destination: str, date_range_start: str,
               date_range_end: str, min_trip_length: int, max_trip_length: int,
               currency: str) -> list[FlightOffer]:
        """return offers found within the flexible departure and trip-length window."""
