from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_chart(rows: list[dict], output: Path = Path("data/price-history.png")) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6))
    destinations = sorted({row["destination"] for row in rows})
    plotted = False
    for destination in destinations:
        series = sorted((row for row in rows if row["destination"] == destination),
                        key=lambda row: row["observed_on"])
        by_day = {}
        for row in series:
            day = row["observed_on"]
            by_day[day] = min(float(row["price"]), by_day.get(day, float("inf")))
        if by_day:
            ax.plot(list(by_day.keys()), list(by_day.values()), marker="o", label=destination)
            plotted = True
    ax.set_title("Northern Lights Trip — Round-Trip Flight Price History")
    ax.set_xlabel("Date checked")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.3)
    if plotted:
        ax.legend(title="Destination")
        fig.autofmt_xdate(rotation=35)
    else:
        ax.text(0.5, 0.5, "No flight prices recorded yet", ha="center", va="center",
                transform=ax.transAxes)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
