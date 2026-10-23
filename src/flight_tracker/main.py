"""run flexible-date flight searches and publish the best fare for each route."""

from datetime import datetime, timezone
from pathlib import Path

from .chart import render_chart
from .config import Config
from .discord_client import DiscordClient
from .history import load_history, previous_by_route, record_offers
from .providers.serpapi import SerpApiProvider


def main() -> None:
    config = Config.from_env()
    provider = SerpApiProvider(config.serpapi_api_key, config.country, config.language)
    todays_offers = []
    failures = []
    for origin in config.origins:
        for destination in config.destinations:
            try:
                offers = provider.search(origin, destination, config.date_range_start, config.date_range_end,
                                         config.min_trip_length, config.max_trip_length, config.currency)
                todays_offers.extend(offers)
                best = min(offers, key=lambda offer: offer.price) if offers else None
                if best:
                    print(f"{origin}->{destination}: {len(offers)} offers; best {best.price:.0f} {best.currency} ({best.departure_date} to {best.return_date})")
                else:
                    print(f"{origin}->{destination}: no offers returned")
            except Exception as exc:
                failures.append(f"{origin}->{destination}: {exc}")
                print(f"search failed for {origin}->{destination}: {exc}")

    if not todays_offers:
        raise RuntimeError("no flight offers returned. " + " | ".join(failures))

    selected = {}
    for offer in todays_offers:
        key = (offer.origin, offer.destination)
        if key not in selected or offer.price < selected[key].price:
            selected[key] = offer

    observed_on = datetime.now(timezone.utc).isoformat(timespec="minutes")
    previous = previous_by_route(load_history(), observed_on)
    rows = record_offers(selected.values(), observed_on)
    render_chart(rows)

    lines = ["**northern lights flight tracker**", f"origins: {', '.join(config.origins)}",
             f"travel window: {config.date_range_start} to {config.date_range_end}",
             f"trip length: {config.min_trip_length}-{config.max_trip_length} days · checked {observed_on} UTC"]
    alerts = []
    for origin in config.origins:
        for destination in config.destinations:
            key = (origin, destination)
            offer = selected.get(key)
            if not offer:
                lines.append(f"**{origin} → {destination}:** no offers returned")
                continue
            departure = offer.departure_date[5:]
            returning = offer.return_date[5:]
            lines.append(f"**{origin}→{destination} {offer.currency} {offer.price:.0f}** · "
                         f"{departure}–{returning}")
            prior = previous.get(key)
            reasons = []
            if offer.price <= config.min_alert_price:
                reasons.append(f"at or below {config.min_alert_price:.0f} {offer.currency}")
            if prior and float(prior["price"]) - offer.price >= config.price_drop_alert:
                reasons.append(f"down {float(prior['price']) - offer.price:.0f} {offer.currency} since last check")
            if reasons:
                alerts.append(f"**{origin} → {destination}** is {offer.currency} {offer.price:.0f} "
                              f"({offer.departure_date} to {offer.return_date}): {', '.join(reasons)}.")

    if failures:
        lines.append("search warnings: " + "; ".join(failures))
    lines.append("_Cheapest fare found in the flexible window; prices may change before booking._")
    discord = DiscordClient(config.discord_bot_token, config.discord_channel_id_2, config.discord_channel_id_1)
    discord.upsert_tracker_message("\n".join(lines), Path("data/price-history.png"))
    for alert in alerts:
        discord.send_alert(config.discord_user_id, "flight deal: " + alert)


if __name__ == "__main__":
    main()
