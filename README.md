# flight tracker

tracks round-trip flight prices for late january to early february 2027 across flexible arctic destinations. records daily observations, charts price history, updates one discord message, and sends alerts when configured thresholds are met.

## stack

- python 3.12 for orchestration and data processing
- serpapi google flights api behind a replaceable provider interface
- json for persistent price history and discord message metadata
- matplotlib for price chart generation
- requests for serpapi and discord rest calls
- github actions for daily scheduled runs
- unittest for automated tests

## repository layout

- `.github/workflows/track-flights.yml`: daily schedule, route settings, price thresholds, and workflow steps
- `src/flight_tracker/main.py`: coordinates search, storage, charting, discord updates, and alerts
- `src/flight_tracker/config.py`: reads settings and secrets from environment variables
- `src/flight_tracker/providers/base.py`: shared offer model and provider interface
- `src/flight_tracker/providers/serpapi.py`: searches google flights through serpapi and normalizes offers
- `src/flight_tracker/history.py`: records daily offers and finds the lowest price by destination
- `src/flight_tracker/chart.py`: renders `data/price-history.png`
- `src/flight_tracker/discord_client.py`: edits one persistent chart message and sends mentions
- `tests/test_history.py`: checks daily price deduplication

## secrets

add these under repository settings, secrets and variables, actions:

- `SERPAPI_API_KEY`
- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID_1`: channel for price-threshold pings
- `DISCORD_CHANNEL_ID_2`: channel for the persistent tracker message and graph
- `DISCORD_USER_ID`

the discord bot needs permission to view and send messages in both channels. In the tracker channel, it also needs read message history and permission to attach files.

## configuration

edit the environment variables in `.github/workflows/track-flights.yml` to set the origin airport, destinations, departure and return dates, currency, and alert thresholds. `MIN_ALERT_PRICE` sends an alert at or below its value. `MAX_ALERT_PRICE` currently also alerts at or below its value, so use it only if that behavior is intended.

## execution

the workflow installs dependencies, runs tests, searches configured routes, records daily prices, renders the chart, updates the persistent discord message, and commits updated history and message metadata. github actions runners are temporary, so the workflow commits state back to the repository.

## implementation notes

- keep provider-specific logic inside `providers/serpapi.py` so another search api can replace it.
- use matplotlib for accurate charts rather than an image-generation model.
- compare prices only when route, dates, and currency match.
- treat returned fares as observations, not guaranteed booking prices.
- keep api keys and bot tokens in github secrets, never in source files.
