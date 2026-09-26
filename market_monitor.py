"""
US Tech Market Monitor
----------------------
Rules-based end-of-session monitor for U.S. technology stocks.

Outputs:
  - market_report_YYYYMMDD.txt
  - market_report_YYYYMMDD.csv

This project describes price/volume conditions. It does not claim to
identify institutional activity and does not generate buy/sell advice.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf


TICKERS = ["GLW", "KLAC", "SPCX", "VRT"]

LOOKBACK = "18mo"
VOLUME_WINDOW = 20
BREAKOUT_WINDOW = 20
RSI_WINDOW = 14
ATR_WINDOW = 14


@dataclass
class Signal:
    ticker: str
    close: float
    day_change_pct: float
    rvol20: float
    rsi14: float
    ema20: float
    ema50: float
    ema200: float
    prior_20d_high: float
    breakout_pct: float
    atr14_pct: float
    score: float
    label: str
    evidence: str


def calculate_rsi(close: pd.Series, period: int = RSI_WINDOW) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calculate_atr(df: pd.DataFrame, period: int = ATR_WINDOW) -> pd.Series:
    previous_close = df["Close"].shift(1)

    true_range = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - previous_close).abs(),
            (df["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def download_daily_data(ticker: str) -> pd.DataFrame:
    data = yf.download(
        ticker,
        period=LOOKBACK,
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if data.empty:
        raise ValueError(f"No data returned for {ticker}")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    columns = ["Open", "High", "Low", "Close", "Volume"]
    return data[columns].dropna().copy()


def score_stock(ticker: str, df: pd.DataFrame) -> Signal:
    close = df["Close"]
    volume = df["Volume"]

    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()

    rsi14 = calculate_rsi(close)
    atr14 = calculate_atr(df)

    average_volume = volume.rolling(VOLUME_WINDOW).mean()
    rvol20 = volume / average_volume

    # Exclude today's bar so the comparison is genuinely "breakout vs prior high".
    prior_20d_high = close.shift(1).rolling(BREAKOUT_WINDOW).max()
    breakout_pct = close / prior_20d_high - 1

    latest_close = float(close.iloc[-1])
    latest_rvol = float(rvol20.iloc[-1])
    latest_rsi = float(rsi14.iloc[-1])
    latest_breakout = float(breakout_pct.iloc[-1])

    score = 0.0
    evidence: list[str] = []

    # Trend: 25 points.
    if latest_close > ema20.iloc[-1]:
        score += 8
        evidence.append("close > EMA20")
    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 8
        evidence.append("EMA20 > EMA50")
    if latest_close > ema200.iloc[-1]:
        score += 9
        evidence.append("close > EMA200")

    # Volume: 25 points.
    if latest_rvol >= 2.0:
        score += 25
        evidence.append(f"very high volume (RVOL20 {latest_rvol:.2f})")
    elif latest_rvol >= 1.5:
        score += 20
        evidence.append(f"high volume (RVOL20 {latest_rvol:.2f})")
    elif latest_rvol >= 1.2:
        score += 12
        evidence.append(f"above-average volume (RVOL20 {latest_rvol:.2f})")
    elif latest_rvol >= 1.0:
        score += 6
        evidence.append(f"normal/slightly high volume (RVOL20 {latest_rvol:.2f})")

    # Breakout: 20 points.
    if latest_breakout >= 0.03:
        score += 20
        evidence.append("close >3% above prior 20-day high")
    elif latest_breakout >= 0:
        score += 12
        evidence.append("close above prior 20-day high")
    elif latest_breakout >= -0.02:
        score += 5
        evidence.append("close within 2% of prior 20-day high")

    # Momentum: 15 points.
    if 55 <= latest_rsi <= 70:
        score += 15
        evidence.append(f"RSI14 {latest_rsi:.1f}")
    elif 50 <= latest_rsi < 55 or 70 < latest_rsi <= 75:
        score += 9
        evidence.append(f"moderate RSI14 {latest_rsi:.1f}")
    elif latest_rsi > 75:
        score += 4
        evidence.append(f"extended RSI14 {latest_rsi:.1f}")

    # Relative-strength proxy: 15 points.
    return_5d = float(close.pct_change(5).iloc[-1])
    return_20d = float(close.pct_change(20).iloc[-1])

    if return_5d > 0:
        score += 7
    if return_20d > 0:
        score += 8

    if return_5d > 0 and return_20d > 0:
        evidence.append("positive 5d and 20d returns")

    label = (
        "STRONG PRICE/VOLUME"
        if score >= 75
        else "POSITIVE"
        if score >= 60
        else "WATCH"
        if score >= 45
        else "WEAK"
    )

    return Signal(
        ticker=ticker,
        close=latest_close,
        day_change_pct=float(close.pct_change().iloc[-1] * 100),
        rvol20=latest_rvol,
        rsi14=latest_rsi,
        ema20=float(ema20.iloc[-1]),
        ema50=float(ema50.iloc[-1]),
        ema200=float(ema200.iloc[-1]),
        prior_20d_high=float(prior_20d_high.iloc[-1]),
        breakout_pct=latest_breakout * 100,
        atr14_pct=float(atr14.iloc[-1] / latest_close * 100),
        score=round(score, 1),
        label=label,
        evidence="; ".join(evidence),
    )


def build_report(results: list[Signal]) -> str:
    results = sorted(results, key=lambda item: item.score, reverse=True)

    positive = sum(item.day_change_pct > 0 for item in results)
    high_volume = sum(item.rvol20 >= 1.5 for item in results)
    breakouts = sum(item.breakout_pct >= 0 for item in results)

    today_et = datetime.now(ZoneInfo("America/New_York"))

    lines = [
        f"US Tech Market Monitor — {today_et:%Y-%m-%d}",
        "",
        f"Universe: {len(results)} | Positive: {positive}/{len(results)} | "
        f"RVOL20 >= 1.5: {high_volume}/{len(results)} | "
        f"At/above prior 20-day high: {breakouts}/{len(results)}",
        "",
        "Ticker | Close | Day% | RVOL20 | RSI14 | Score | Signal",
        "-" * 74,
    ]

    for item in results:
        lines.append(
            f"{item.ticker:5} | {item.close:8.2f} | "
            f"{item.day_change_pct:+6.2f}% | {item.rvol20:6.2f} | "
            f"{item.rsi14:5.1f} | {item.score:5.1f} | {item.label}"
        )

    lines += ["", "Evidence:"]

    for item in results:
        lines.append(f"- {item.ticker}: {item.evidence or 'No qualifying evidence.'}")

    lines += [
        "",
        "Methodology note:",
        "The score summarizes observable price, volume, trend, breakout, and momentum conditions.",
        "It does not prove institutional buying/selling and is not a trading recommendation.",
    ]

    return "\n".join(lines)


def main() -> None:
    results: list[Signal] = []

    for ticker in TICKERS:
        try:
            data = download_daily_data(ticker)
            results.append(score_stock(ticker, data))
        except Exception as exc:
            print(f"[WARN] {ticker}: {exc}")

    if not results:
        raise RuntimeError("No market data was available.")

    report = build_report(results)
    print(report)

    date_string = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d")

    with open(f"market_report_{date_string}.txt", "w", encoding="utf-8") as file:
        file.write(report)

    pd.DataFrame([asdict(item) for item in results]).to_csv(
        f"market_report_{date_string}.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
