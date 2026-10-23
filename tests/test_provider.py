import unittest
from unittest.mock import Mock, patch

from src.flight_tracker.providers.serpapi import SerpApiProvider


class SerpApiProviderTests(unittest.TestCase):
    @patch("src.flight_tracker.providers.serpapi.requests.get")
    def test_normalizes_flexible_round_trip_offers(self, get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"deals": [
            {"price": 642, "flight_link": "https://example.com/flight", "start_date": "2027-01-26",
             "end_date": "2027-01-30", "arrival_airport_code": "TOS", "airline": "Example Air"},
            {"price": 500, "start_date": "2027-01-26", "end_date": "2027-01-28",
             "arrival_airport_code": "TOS"},
            {"price": 100, "start_date": "2027-01-26", "end_date": "2027-01-30",
             "arrival_airport_code": "KEF"},
        ]}
        get.return_value = response
        offers = SerpApiProvider("test-key").search("IAD", "TOS", "2027-01-25", "2027-02-05", 3, 11, "USD")
        self.assertEqual(len(offers), 1)
        self.assertEqual((offers[0].origin, offers[0].destination, offers[0].price), ("IAD", "TOS", 642.0))
        self.assertEqual((offers[0].departure_date, offers[0].return_date), ("2027-01-26", "2027-01-30"))
        params = get.call_args.kwargs["params"]
        self.assertEqual(params["engine"], "google_flights_deals")
        self.assertEqual(params["outbound_date"], "2027-01-25,2027-02-05")
        self.assertEqual(params["return_date"], "2027-01-25,2027-02-05")
        self.assertEqual(params["query"], "Tromso Norway")


if __name__ == "__main__":
    unittest.main()
