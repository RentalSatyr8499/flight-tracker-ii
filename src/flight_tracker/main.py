"""run the daily flight search and publish results."""

from datetime import date
from pathlib import Path

from .chart import render_chart
from .config import Config
from .discord_client import DiscordClient
from .history import cheapest_by_destination, load_history, record_offers
from .providers.serpapi import SerpApiProvider


def main() -> None:
    """search routes, record prices, refresh the chart, and send alerts."""
    config = Config.from_env()
    provider = SerpApiProvider(config.serpapi_api_key, config.country, config.language)
    todays_offers = []
    failures = []
    for destination in config.destinations:
        try:
            offers = provider.search(config.origin, destination, config.departure_date,
                                     config.return_date, config.currency)
            todays_offers.extend(offers)
            print(f"{destination}: {len(offers)} offers")
        except Exception as exc:
            failures.append(f"{destination}: {exc}")
            print(f"search failed for {destination}: {exc}")

    if not todays_offers:
        raise RuntimeError("no flight offers returned. " + " | ".join(failures))

    rows = record_offers(todays_offers, date.today().isoformat())
    render_chart(rows)
    cheapest = cheapest_by_destination(rows)
    current = {}
    for offer in todays_offers:
        row = {
            "destination": offer.destination, "price": offer.price,
            "currency": offer.currency, "booking_url": offer.booking_url,
            "airline_summary": offer.airline_summary,
        }
        if offer.destination not in current or offer.price < current[offer.destination]["price"]:
            current[offer.destination] = row

    lines = [
        f"**northern lights flight tracker**",
        f"route: {config.origin} to flexible arctic destinations",
        f"dates: {config.departure_date} to {config.return_date} · checked {date.today().isoformat()}",
    ]
    for destination in config.destinations:
        offer = current.get(destination)
        if offer:
            link = f" · [flights]({offer['booking_url']})" if offer["booking_url"] else ""
            airline = f" | {offer['airline_summary']}" if offer["airline_summary"] else ""
            lines.append(f"**{destination}: {offer['currency']} {offer['price']:.0f}**{airline}{link}")
        else:
            lines.append(f"**{destination}:** no offers returned today")
    if failures:
        lines.append("search warnings: " + "; ".join(failures))
    lines.append("_price history is attached; prices can change before booking._")
    discord = DiscordClient(config.discord_bot_token, config.discord_channel_id_2, config.discord_channel_id_1)
    discord.upsert_tracker_message("\n".join(lines), Path("data/price-history.png"))

    for destination, offer in current.items():
        if config.min_alert_price is not None and offer["price"] <= config.min_alert_price:
            discord.send_alert(config.discord_user_id,
                f"flight deal: **{destination}** is {offer['currency']} {offer['price']:.0f}, at or below your {config.min_alert_price:.0f} threshold.")
        if config.max_alert_price is not None and offer["price"] <= config.max_alert_price:
            discord.send_alert(config.discord_user_id,
                f"price threshold reached for **{destination}**: {offer['currency']} {offer['price']:.0f} (configured threshold {config.max_alert_price:.0f}).")


if __name__ == "__main__":
    main()
