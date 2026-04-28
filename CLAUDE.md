# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
.venv/bin/python main.py
```

The FastAPI backend must be running at `localhost:8000` before launching. The backend repo is at `~/PycharmProjects/demo_stock_trading_full_backend`.

## Building UI files

After editing any `.ui` file in `ui/`, regenerate its Python counterpart:

```bash
.venv/bin/pyuic5 ui/<name>.ui -o ui/generated/<name>_ui.py
```

Never edit files in `ui/generated/` by hand — they are always overwritten by `pyuic5`.

**Layout margin gotcha:** Qt Designer's XML parser requires four separate properties — `leftMargin`, `topMargin`, `rightMargin`, `bottomMargin` — on layout elements. A single `contentsMargins` block with multiple `<number>` children will throw a `TypeError` at load time.

## Architecture

The app follows **MVP (Model-View-Presenter)**:

- **`ui/*.ui`** — Qt Designer XML, one file per screen. The only place layout is defined. Must remain editable in Qt Designer.
- **`ui/generated/`** — `pyuic5` output. Views inherit from these classes via multiple inheritance.
- **`views/`** — Thin Qt widgets. Load the `.ui` file via `uic.loadUi(...)`, wire signals to presenter callbacks, expose a minimal API the presenter calls to update the UI. Zero business logic, zero `httpx` imports.
- **`presenters/`** — One presenter per screen. Receives events from the view, makes `async` API calls via services, calls back into the view with results. All coroutines; never blocks the event loop.
- **`services/api_client.py`** — Single `APIClient` instance (`api_client`). Every backend endpoint is an `async` method returning raw `dict`. Raises `APIError(status_code, detail)` on HTTP ≥ 400.
- **`services/auth_service.py`** — Single `AuthService` instance (`auth_service`). Owns token lifecycle: login, refresh, logout, keyring read/write. Sets the bearer token on `api_client` after every successful auth.
- **`models/`** — Pydantic v2 models matching backend response shapes. Used for typed parsing in presenters; services return raw `dict`.
- **`styles/theme.qss`** — All visual styling. Widget appearance is controlled via `objectName` (e.g., `objectName="btnPrimary"`). Never hardcode colors or fonts in Python.

## Async rules

- The event loop is `qasync.QEventLoop`. It is set as the running loop in `main.py` before any view is instantiated.
- Qt slots that trigger API calls must be `async def` and scheduled with `asyncio.ensure_future(coro())` from the synchronous signal handler.
- No `QThread`, no `concurrent.futures`, no `time.sleep`. Every blocking operation is an `await`.

## Adding a new screen

1. Create `ui/<screen>.ui` in Qt Designer (or by hand as XML).
2. Run `pyuic5` to generate `ui/generated/<screen>_ui.py`.
3. Create `views/<screen>_view.py` — inherit from both `QWidget` (or `QMainWindow`) and the generated class; call `self.setupUi(self)`; expose a presenter-friendly API.
4. Create `presenters/<screen>_presenter.py` — inject the view in `__init__`; implement `async` handler methods.
5. Add navigation: the previous screen's presenter imports the new view and opens it, then closes itself.

## Design system

All component styles are defined in `styles/theme.qss` keyed by `objectName`. Key names in use:

| objectName | Component |
|---|---|
| `btnPrimary` / `btnSecondary` | Standard action buttons |
| `btnBuy` / `btnSell` | Trade action buttons (green / red) |
| `btnGhost` / `btnDanger` | Tertiary / destructive actions |
| `navItem` / `navItemActive` | Sidebar navigation items |
| `card` / `statCard` / `loginCard` | Surface containers |
| `priceUp` / `priceDown` / `priceNeutral` | Monospace price labels |
| `bigValue` / `statValue` / `statLabel` | Dashboard stat widget labels |
| `badgeOpen` / `badgeClosed` / `badgeNeutral` | Status badges |
| `errorLabel` / `successLabel` | Inline form feedback |
