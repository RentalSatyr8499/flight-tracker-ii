# flight tracker

Tracks round-trip fares according to `track-flights.yml`. Each run searches a flexible travel window, records the cheapest returned itinerary for every origin/destination pair, charts history, and updates one persistent Discord message. It pings the configured user only when a route is at or below the price floor or drops by the configured amount since the prior observation.

<img width="816" height="144" alt="image" src="https://github.com/user-attachments/assets/ed9dcc2b-38d4-4cb6-b083-d41fda31f960" />
<img width="906" height="738" alt="image" src="https://github.com/user-attachments/assets/edc44c10-4b93-4f6e-b69a-4786de8ab751" />

## stack

- Python 3.12, SerpApi Google Flights Deals flexible-date search, requests, Matplotlib, JSON, GitHub Actions, and unittest

## repository layout

- `.github/workflows/track-flights.yml`: schedule, airport lists, date window, trip length, and alert thresholds
- `src/flight_tracker/main.py`: searches, stores best offers, updates Discord, and sends conditional alerts
- `src/flight_tracker/config.py`: settings and secrets
- `src/flight_tracker/providers/base.py`: normalized offer model and provider contract
- `src/flight_tracker/providers/serpapi.py`: flexible-date search and offer normalization
- `src/flight_tracker/history.py`: cheapest selected fare per route and previous observations
- `src/flight_tracker/chart.py`: price-history chart
- `src/flight_tracker/discord_client.py`: persistent tracker message and user mentions
- `tests/`: unit tests

## secrets

Add these under repository settings → secrets and variables → actions:

- `SERPAPI_API_KEY`
- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID_1`: channel for conditional price-alert pings
- `DISCORD_CHANNEL_ID_2`: channel for the persistent tracker message and graph
- `DISCORD_USER_ID`

The bot needs permission to view and send messages in both channels. In the tracker channel, it also needs read message history and permission to attach files.

## configuration

Edit `.github/workflows/track-flights.yml`: `ORIGIN_AIRPORTS` is currently IAD,RIC; `DESTINATION_AIRPORTS` lists the northern destinations; `DATE_RANGE_START` and `DATE_RANGE_END` define the allowed outbound-and-return travel window; `MIN_TRIP_LENGTH` is the minimum trip length (3 days); `MAX_TRIP_LENGTH` is the maximum (11 days); `MIN_ALERT_PRICE` triggers a ping at or below $500; and `PRICE_DROP_ALERT` triggers a ping when the route price falls by at least $50 since its previous observation.

The workflow runs at 7 a.m. and 10 p.m. US Eastern Standard Time (12:00 and 03:00 UTC). GitHub Actions cron uses UTC, so adjust the hours if you want to follow daylight-saving time. Every successful run updates the tracker message; only matching alert conditions trigger a user mention.

## execution

The workflow installs dependencies, runs tests, searches all origin/destination pairs, records each route's cheapest eligible fare and actual departure/return dates, renders the chart, updates Discord, and commits history and message metadata. Fare results are observations, not guaranteed booking prices.
