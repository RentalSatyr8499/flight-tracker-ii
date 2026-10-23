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

## to use
1. Create a [SerpApi account](https://serpapi.com/) and obtain an API key. The tracker uses SerpApi to search Google Flights, so make sure your account has access to the required search engine and that you understand its request limits.

2. Create a Discord bot in the [Discord Developer Portal](https://discord.com/developers/applications). Add the bot to your server and give it permission to view and send messages in both the price-alert channel and the tracker channel. In the tracker channel, it also needs permission to read message history and attach files.

3. Copy the Discord bot token from the Developer Portal. Enable Developer Mode in Discord, then right-click the relevant channels and your user profile to copy the channel IDs and user ID.

4. Open your GitHub repository and navigate to Settings → Secrets and variables → Actions. Add the following repository secrets: `SERPAPI_API_KEY`, `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID_1` (the channel for conditional price-alert pings), `DISCORD_CHANNEL_ID_2` (the channel for the persistent tracker message and graph), and `DISCORD_USER_ID`. Paste the corresponding values into each secret. Keep these values private and do not commit them to the repository.

5. Open `.github/workflows/track-flights.yml` and edit the environment variables under the `track` job to configure the tracker. `ORIGIN_AIRPORTS` is a comma-separated list of departure airports, such as `IAD,RIC`; `DESTINATION_AIRPORTS` is a comma-separated list of destination airports, such as `TOS,KEF,HEL`. Use airport codes supported by Google Flights. The tracker searches each origin/destination combination.

6. Set `DATE_RANGE_START` and `DATE_RANGE_END` to define the desired travel window, using `YYYY-MM-DD` format. For example, `2027-01-25` and `2027-02-05` define the January 25–February 5, 2027 window. Set `MIN_TRIP_LENGTH` and `MAX_TRIP_LENGTH` to constrain the allowed trip duration in days. Set `CURRENCY` to the desired fare currency, `SERPAPI_COUNTRY` to the country code used for the search, and `SERPAPI_LANGUAGE` to the desired language.

7. Configure the alert thresholds in the same workflow file. `MIN_ALERT_PRICE` triggers a user mention when a fare is at or below the specified price, while `PRICE_DROP_ALERT` triggers a mention when a route's price falls by at least the specified amount since its previous observation. The configured currency applies to these thresholds.

8. Configure when the tracker runs by editing the `schedule` cron expression in `.github/workflows/track-flights.yml`. GitHub Actions cron expressions use UTC. For example, `0 12,3 * * *` runs daily at 12:00 UTC and 03:00 UTC, corresponding to 7 a.m. and 10 p.m. Eastern Standard Time, respectively. These times shift relative to Eastern local time during daylight-saving time. Use a [cron expression generator](https://crontab.guru/) if needed, and remember that the first field is the minute and the second is the hour.

9. Commit and push your configuration changes to the repository's `main` branch. The workflow installs dependencies, runs the unit tests, searches the configured routes, records the cheapest eligible fares, renders the price-history chart, updates the persistent Discord message, and commits updated history and message metadata.

10. To run the tracker manually, open the repository's Actions tab, select **track flight prices**, click **Run workflow**, and confirm the run. The same workflow runs automatically according to its configured schedule. Check the workflow run logs if a run fails or produces unexpected results.

11. Each successful run updates the persistent Discord tracker message and records fare observations. A user mention is sent only when a configured alert condition is met. Results reflect the fares returned by the search provider; prices and availability may change before booking.
