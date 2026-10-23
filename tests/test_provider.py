import unittest
from unittest.mock import Mock, patch

from src.flight_tracker.providers.serpapi import SerpApiProvider


class SerpApiProviderTests(unittest.TestCase):
    @patch("src.flight_tracker.providers.serpapi.requests.get")
    def test_normalizes_flexible_round_trip_offers(self, get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"best_flights": [{
            "price": 642, "link": "https://example.com/flight",
            "flights": [
                {"airline": "Example Air", "departure_airport": {"date": "2027-01-26 10:00"}},
                {"airline": "Northern Air", "departure_airport": {"date": "2027-01-30 10:00"}},
            ]}], "other_flights": [{"price": None, "flights": []}]}
        get.return_value = response
        offers = SerpApiProvider("test-key").search("IAD", "TOS", "2027-01-25", "2027-02-05", 3, 11, "USD")
        self.assertEqual(len(offers), 1)
        self.assertEqual((offers[0].origin, offers[0].destination, offers[0].price), ("IAD", "TOS", 642.0))
        self.assertEqual((offers[0].departure_date, offers[0].return_date), ("2027-01-26", "2027-01-30"))
        self.assertEqual(get.call_args.kwargs["params"]["outbound_date"], "2027-01-25,2027-02-05")
        self.assertEqual(get.call_args.kwargs["params"]["trip_length"], "3,11")


if __name__ == "__main__":
    unittest.main()
