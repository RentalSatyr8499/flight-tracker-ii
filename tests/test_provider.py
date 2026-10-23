import unittest
from unittest.mock import Mock, patch

from src.flight_tracker.providers.serpapi import SerpApiProvider


class SerpApiProviderTests(unittest.TestCase):
    @patch("src.flight_tracker.providers.serpapi.requests.get")
    def test_normalizes_round_trip_offers(self, get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "best_flights": [{
                "price": 642,
                "link": "https://example.com/flight",
                "flights": [
                    {"airline": "Example Air"},
                    {"airline": "Northern Air"},
                    {"airline": "Example Air"},
                ],
            }],
            "other_flights": [{"price": None, "flights": []}],
        }
        get.return_value = response

        provider = SerpApiProvider("test-key")
        offers = provider.search("IAD", "TOS", "2027-01-25", "2027-02-05", "USD")

        self.assertEqual(len(offers), 1)
        self.assertEqual(offers[0].origin, "IAD")
        self.assertEqual(offers[0].destination, "TOS")
        self.assertEqual(offers[0].price, 642.0)
        self.assertEqual(offers[0].airline_summary, "Example Air, Northern Air")
        self.assertEqual(offers[0].booking_url, "https://example.com/flight")
        self.assertEqual(get.call_args.kwargs["params"]["type"], "1")
        self.assertEqual(get.call_args.kwargs["params"]["return_date"], "2027-02-05")


if __name__ == "__main__":
    unittest.main()
