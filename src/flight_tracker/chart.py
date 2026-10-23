from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_chart(rows: list[dict], output: Path = Path("data/price-history.png")) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    routes = sorted({(row["origin"], row["destination"]) for row in rows})
    plotted = False
    for origin, destination in routes:
        series = sorted((row for row in rows if row["origin"] == origin and row["destination"] == destination),
                        key=lambda row: row["observed_on"])
        by_day = {}
        for row in series:
            day = row["observed_on"][:10]
            by_day[day] = min(float(row["price"]), by_day.get(day, float("inf")))
        if by_day:
            ax.plot(list(by_day.keys()), list(by_day.values()), marker="o", label=f"{origin} → {destination}")
            plotted = True
    ax.set_title("Northern Lights Trip — Cheapest Round-Trip Fare by Route")
    ax.set_xlabel("Date checked")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.3)
    if plotted:
        ax.legend(title="Origin → destination", fontsize="small", ncol=2)
        fig.autofmt_xdate(rotation=35)
    else:
        ax.text(0.5, 0.5, "No flight prices recorded yet", ha="center", va="center",
                transform=ax.transAxes)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
