# US Tech Market Monitor

A transparent, rules-based daily market monitor for U.S. technology and semiconductor stocks.

![Daily Market Monitor](https://github.com/YOUR_USERNAME/us-tech-market-monitor/actions/workflows/daily-market-monitor.yml/badge.svg)

## Latest signals

These signal badges are regenerated automatically after each scheduled end-of-session run.


| KLAC                                                                                                                                                                                 | ALAB                                                                                                                                                                                 | SPCX                                                                                                                                                                                 | TSLA                                                                                                                                                                                 | VRT                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ![KLAC](vscode-file://vscode-app/c:/Users/admin/AppData/Local/Temp/515a4975-f270-4ee7-95af-6918fd35047a_us-tech-market-monitor-KLAC-ALAB-SPCX-TSLA-VRT.zip.47a/docs/badges/KLAC.svg) | ![ALAB](vscode-file://vscode-app/c:/Users/admin/AppData/Local/Temp/515a4975-f270-4ee7-95af-6918fd35047a_us-tech-market-monitor-KLAC-ALAB-SPCX-TSLA-VRT.zip.47a/docs/badges/ALAB.svg) | ![SPCX](vscode-file://vscode-app/c:/Users/admin/AppData/Local/Temp/515a4975-f270-4ee7-95af-6918fd35047a_us-tech-market-monitor-KLAC-ALAB-SPCX-TSLA-VRT.zip.47a/docs/badges/SPCX.svg) | ![TSLA](vscode-file://vscode-app/c:/Users/admin/AppData/Local/Temp/515a4975-f270-4ee7-95af-6918fd35047a_us-tech-market-monitor-KLAC-ALAB-SPCX-TSLA-VRT.zip.47a/docs/badges/TSLA.svg) | ![VRT](vscode-file://vscode-app/c:/Users/admin/AppData/Local/Temp/515a4975-f270-4ee7-95af-6918fd35047a_us-tech-market-monitor-KLAC-ALAB-SPCX-TSLA-VRT.zip.47a/docs/badges/VRT.svg) |


**Open the full dashboard →**

> The badges are descriptive model signals, not buy/sell recommendations and not proof of institutional activity.



## What it measures

The project is designed to answer a specific question:

> **Is a market move supported by price, volume, trend, and breakout behavior?**

It is a **monitoring and research tool**, not a trading system and not proof of institutional buying or selling.

## Features

- Daily price change
- 20-day relative volume (RVOL20)
- EMA20 / EMA50 / EMA200 trend structure
- RSI14 momentum
- Prior 20-session high and breakout distance
- ATR14 volatility
- Transparent 0–100 price/volume alignment score
- Human-readable daily report
- CSV output for further analysis
- GitHub Actions automation after the U.S. regular session
- README badges and a dashboard for five tracked names: `KLAC`, `ALAB`, `SPCX`, `TSLA`, `VRT`



## Default universe

`KLAC`, `ALAB`, `SPCX`, `TSLA`, `VRT`

The monitor can easily be customized by editing `TICKERS` in `market_monitor.py`.

## Scoring model

The score is deliberately transparent:


| Component               | Weight  | What it measures                       |
| ----------------------- | ------- | -------------------------------------- |
| Trend                   | 25      | Close vs EMA20/200 and EMA20 vs EMA50  |
| Volume                  | 25      | RVOL20                                 |
| Breakout                | 20      | Distance above/below prior 20-day high |
| Momentum                | 15      | RSI14                                  |
| Relative strength proxy | 15      | Positive 5-day and 20-day returns      |
| **Total**               | **100** |                                        |




### Signal labels

- **STRONG PRICE/VOLUME**: 75–100
- **POSITIVE**: 60–74.9
- **WATCH**: 45–59.9
- **WEAK**: below 45

These labels describe the model's inputs. They are **not buy/sell recommendations**.

## Run locally

```bash
git clone https://github.com/clairechen163/us-tech-market-monitor.git
cd us-tech-market-monitor

python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows

pip install -r requirements.txt
python market_monitor.py
python scripts/update_dashboard.py
```

The monitor writes:

- `market_report_YYYYMMDD.txt`
- `market_report_YYYYMMDD.csv`

The dashboard updater reads the latest CSV and generates:

- `docs/dashboard.md`
- `docs/badges/KLAC.svg`
- `docs/badges/ALAB.svg`
- `docs/badges/SPCX.svg`
- `docs/badges/TSLA.svg`
- `docs/badges/VRT.svg`



## GitHub Actions

The workflow runs on weekdays after the U.S. regular session. It runs the market monitor, updates the five signal badges/dashboard, and commits changed dashboard assets back to the repository.

GitHub Actions uses UTC. The schedule is intentionally set late enough to be after the 16:00 ET close during both daylight-saving and standard-time periods.

You can also run it manually from:

**GitHub → Actions → Daily Market Monitor → Run workflow**

### One-time setup

Replace `YOUR_USERNAME` in the workflow-status badge URL near the top of this README with your GitHub username or organization name.

The workflow-status badge is separate from the five market-signal badges: GitHub's native status badge reports whether the workflow is passing/failing, while the five local SVGs report the latest model signal.

If your repository uses branch protection, make sure GitHub Actions is permitted to push the generated dashboard files.

## Example interpretation

A stock that rises strongly while:

- RVOL20 is above 1.5,
- price is above EMA20 and EMA50,
- and price breaks the prior 20-day high

has stronger **price/volume confirmation** than a stock that rises on below-average volume.

The model does **not** infer that a particular institution is buying. Public OHLCV data cannot establish that conclusion by itself.

## Data source

The project uses `[yfinance](https://github.com/ranaroussi/yfinance)` for market data.

Yahoo Finance data availability, adjustments, rate limits, and historical-data behavior can change. For production or trading use, consider replacing the data layer with a licensed market-data provider.

## Limitations

- This is a daily end-of-session screen, not a real-time trading engine.
- RVOL is calculated against the previous 20 sessions.
- Technical indicators are descriptive, not predictive guarantees.
- News and fundamental catalysts are not automatically verified by this script.
- Data-provider outages or changes can cause missing symbols or incomplete reports.
- The model intentionally avoids claiming that volume alone identifies institutional activity.



## License

MIT