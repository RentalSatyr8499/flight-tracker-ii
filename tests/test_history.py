import tempfile
import unittest
from pathlib import Path

from src.flight_tracker.history import record_offers
from src.flight_tracker.providers.base import FlightOffer


class HistoryTests(unittest.TestCase):
    def test_records_and_keeps_lowest_price_per_day_route(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            offers = [
                FlightOffer("IAD", "TOS", "2027-01-25", "2027-02-05", 900, "USD"),
                FlightOffer("IAD", "TOS", "2027-01-25", "2027-02-05", 850, "USD"),
            ]
            rows = record_offers(offers, "2026-10-23", path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["price"], 850)


if __name__ == "__main__":
    unittest.main()
