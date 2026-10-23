import tempfile
import unittest
from pathlib import Path

from src.flight_tracker.history import previous_by_route, record_offers
from src.flight_tracker.providers.base import FlightOffer


class HistoryTests(unittest.TestCase):
    def test_records_cheapest_offer_per_day_and_route(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            offers = [FlightOffer("IAD", "TOS", "2027-01-25", "2027-01-28", 900, "USD"),
                      FlightOffer("IAD", "TOS", "2027-01-26", "2027-01-30", 850, "USD"),
                      FlightOffer("RIC", "TOS", "2027-01-26", "2027-01-30", 800, "USD")]
            rows = record_offers(offers, "2026-10-23", path)
            self.assertEqual(len(rows), 2)
            iad = next(row for row in rows if row["origin"] == "IAD")
            self.assertEqual(iad["price"], 850)
            self.assertEqual(iad["departure_date"], "2027-01-26")

    def test_previous_prices_are_route_specific(self):
        rows = [{"observed_on": "2026-10-21", "origin": "IAD", "destination": "TOS", "price": 600},
                {"observed_on": "2026-10-22", "origin": "IAD", "destination": "TOS", "price": 700},
                {"observed_on": "2026-10-22", "origin": "RIC", "destination": "TOS", "price": 500}]
        previous = previous_by_route(rows, "2026-10-23")
        self.assertEqual(previous[("IAD", "TOS")]["price"], 700)
        self.assertEqual(previous[("RIC", "TOS")]["price"], 500)


if __name__ == "__main__":
    unittest.main()
