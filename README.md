# Demo Exchange Desktop

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-Desktop_UI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![httpx](https://img.shields.io/badge/httpx-Async_HTTP-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Work_In_Progress-orange?style=for-the-badge)

A native desktop stock trading simulator built with PyQt5. Connects to a [FastAPI backend](https://github.com/eliran/demo_stock_trading_full_backend) to simulate real-time trading with live market data, portfolio tracking, and analyst sentiment.

---

## Pages

| Page | Purpose |
|---|---|
| **Login** | Authenticate with email + password. Tokens are persisted securely via the OS keyring so the session survives restarts. |
| **Register** | Create a new account with full validation (password strength, confirmation match). |
| **Dashboard** | Overview of account value, P&L, market open/close status, and top market movers (gainers & losers). Auto-refreshes every 30 seconds while active. |
| **Portfolio** | Paginated table of current holdings showing symbol, average buy price, last price, total value, and return per position. |
| **Trade** | Look up a live quote by ticker symbol, then place a buy or sell order. Shows OHLV data, estimated order total, and order result inline. |
| **History** | Paginated transaction log of all past buy/sell orders with profit/loss per trade. |
| **Watchlist** | Personal watchlist — add or remove symbols and see live price + change at a glance. |
| **Search** | Search stocks by symbol or name. Select a result to load a detail card with price, OHLV, and analyst sentiment breakdown (Strong Buy → Strong Sell consensus). Add any stock directly to the watchlist from here. |

---

## Architecture

The app follows **MVP (Model-View-Presenter)**:

```
┌─────────────────────────────────────────────────────────┐
│                        Views (PyQt5)                    │
│  Thin QWidget subclasses. Load .ui files at runtime,    │
│  wire Qt signals to presenter callbacks, expose a       │
│  minimal setter API. Zero business logic.               │
└────────────────────┬────────────────────────────────────┘
                     │  events / setter calls
┌────────────────────▼────────────────────────────────────┐
│                     Presenters (async)                  │
│  One per screen. Receive UI events, call services,      │
│  parse responses with Pydantic models, update the view. │
└────────────────────┬────────────────────────────────────┘
                     │  await
┌────────────────────▼────────────────────────────────────┐
│                      Services (httpx)                   │
│  api_client  — single httpx.AsyncClient, every backend  │
│               endpoint is an async method.              │
│  auth_service — token lifecycle: login, refresh,        │
│                 logout, keyring read/write.              │
└─────────────────────────────────────────────────────────┘
```

**Key files:**

```
main.py                        Entry point, event loop setup, session restore
ui/*.ui                        Qt Designer XML — the only place layout is defined
views/                         One view per screen
presenters/                    One presenter per screen
services/api_client.py         All HTTP calls
services/auth_service.py       Token + session management
models/                        Pydantic v2 models matching backend response shapes
styles/theme.qss               All visual styling (objectName-based)
```

---

## Async Event Loop

The app bridges PyQt5's event loop with Python's `asyncio` using **[qasync](https://github.com/CabbageDevelopment/qasync)**:

```python
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)
with loop:
    loop.run_forever()
```

Qt signals that trigger API calls use `asyncio.ensure_future()` from the synchronous signal handler:

```python
self.loginButton.clicked.connect(
    lambda: asyncio.ensure_future(self._presenter.handle_login())
)
```

There are no threads, no `QThread`, no `time.sleep`. Every blocking operation is an `await`.

---

## Design System

All styling is driven by `styles/theme.qss`. Widget appearance is controlled via `objectName` — no colors or fonts are hardcoded in Python.

| `objectName` | Component |
|---|---|
| `btnPrimary` / `btnSecondary` | Standard action buttons |
| `btnBuy` / `btnSell` | Trade action buttons (green / red) |
| `btnGhost` / `btnDanger` | Tertiary / destructive actions |
| `navItem` / `navItemActive` | Sidebar navigation items |
| `card` / `statCard` / `loginCard` | Surface containers |
| `priceUp` / `priceDown` / `priceNeutral` | Monospace price labels |
| `bigValue` / `statValue` / `statLabel` | Dashboard stat widget labels |
| `badgeOpen` / `badgeClosed` / `badgeNeutral` | Market status badges |
| `errorLabel` / `successLabel` | Inline form feedback |
| `heading2` / `heading3` / `subtext` | Typography hierarchy |

Runtime style changes (e.g. switching a price label from neutral → green) use the unpolish/polish cycle:

```python
label.setObjectName("priceUp")
label.style().unpolish(label)
label.style().polish(label)
```

---

## Running from Source

**Prerequisites:** Python 3.12, and the [FastAPI backend](https://github.com/eliran/demo_stock_trading_full_backend) running at `localhost:8000`.

```bash
# Clone and set up
git clone https://github.com/eliran/demo-exchange-desktop
cd demo-exchange-desktop
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py
```

---

## Building an Executable

Uses **PyInstaller** to bundle everything (`.ui` files, QSS theme, assets) into a single binary.

```bash
pip install pyinstaller

# First time — generate the spec (already committed):
pyinstaller --name "DemoExchange" --windowed --onefile main.py

# Subsequent builds — use the spec directly:
pyinstaller DemoExchange.spec
```

Output lands in `dist/DemoExchange` (or `dist/DemoExchange.exe` on Windows).

> **Note:** PyInstaller builds for the OS you run it on. To produce a Windows `.exe`, build on a Windows machine or use a CI runner with a Windows environment (e.g. GitHub Actions).

---

## Requirements

```
PyQt5
qasync
httpx
keyring
pydantic
pyinstaller
```
