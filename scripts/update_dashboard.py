"""Generate README/dashboard signal badges from the latest monitor CSV."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import html

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BADGE_DIR = ROOT / "docs" / "badges"
DASHBOARD = ROOT / "docs" / "dashboard.md"
TICKERS = ["KLAC", "ALAB", "SPCX", "TSLA", "VRT"]

COLORS = {
    "STRONG PRICE/VOLUME": "#2da44e",
    "POSITIVE": "#1f883d",
    "WATCH": "#bf8700",
    "WEAK": "#cf222e",
    "WAITING": "#57606a",
}


def latest_csv() -> Path | None:
    files = sorted(ROOT.glob("market_report_*.csv"))
    return files[-1] if files else None


def badge_svg(ticker: str, label: str, score: str, updated: str) -> str:
    color = COLORS.get(label, COLORS["WAITING"])
    left = html.escape(f"{ticker}  {label}")
    right = html.escape(score)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="28" role="img" aria-label="{html.escape(ticker)} signal {html.escape(label)}">
  <title>{html.escape(ticker)} signal: {html.escape(label)} | Score: {html.escape(score)} | Updated: {html.escape(updated)}</title>
  <rect width="220" height="28" rx="4" fill="#f6f8fa"/>
  <rect x="0" y="0" width="156" height="28" rx="4" fill="#24292f"/>
  <rect x="156" y="0" width="64" height="28" rx="4" fill="{color}"/>
  <text x="78" y="18" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="600" fill="#fff">{left}</text>
  <text x="188" y="18" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#fff">{right}</text>
</svg>
'''


def write_waiting_badges() -> None:
    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    for ticker in TICKERS:
        (BADGE_DIR / f"{ticker}.svg").write_text(
            badge_svg(ticker, "WAITING", "--", "No report yet"), encoding="utf-8"
        )


def main() -> None:
    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = latest_csv()

    if csv_path is None:
        write_waiting_badges()
        DASHBOARD.write_text(
            "# Latest Market Signals\n\nNo market report has been generated yet. Run `market_monitor.py` first.\n",
            encoding="utf-8",
        )
        return

    df = pd.read_csv(csv_path)
    df = df[df["ticker"].isin(TICKERS)].set_index("ticker")
    updated = csv_path.stem.replace("market_report_", "")

    rows = []
    for ticker in TICKERS:
        if ticker not in df.index:
            label, score = "WAITING", "--"
            values = {"close": "--", "day_change_pct": "--", "rvol20": "--", "rsi14": "--"}
        else:
            row = df.loc[ticker]
            label = str(row["label"])
            score = f"{float(row['score']):.0f}"
            values = {
                "close": f"{float(row['close']):.2f}",
                "day_change_pct": f"{float(row['day_change_pct']):+.2f}%",
                "rvol20": f"{float(row['rvol20']):.2f}",
                "rsi14": f"{float(row['rsi14']):.1f}",
            }

        (BADGE_DIR / f"{ticker}.svg").write_text(
            badge_svg(ticker, label, score, updated), encoding="utf-8"
        )
        rows.append((ticker, values, score, label))

    lines = [
        "# Latest Market Signals",
        "",
        f"**Last updated:** {updated}",
        "",
        "| " + " | ".join(TICKERS) + " |",
        "|" + "---|" * len(TICKERS),
        "| " + " | ".join(f"![{t}](badges/{t}.svg)" for t in TICKERS) + " |",
        "",
        "## Metrics",
        "",
        "| Ticker | Close | Day % | RVOL20 | RSI14 | Score | Signal |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for ticker, values, score, label in rows:
        lines.append(
            f"| {ticker} | {values['close']} | {values['day_change_pct']} | {values['rvol20']} | {values['rsi14']} | {score} | {label} |"
        )

    lines += [
        "",
        "## Signal definitions",
        "",
        "- **STRONG PRICE/VOLUME:** score 75–100",
        "- **POSITIVE:** score 60–74.9",
        "- **WATCH:** score 45–59.9",
        "- **WEAK:** score below 45",
        "",
        "The signal summarizes observable price, volume, trend, breakout, momentum, and relative-strength conditions. It does **not** prove institutional buying/selling and is not a buy/sell recommendation.",
    ]
    DASHBOARD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
