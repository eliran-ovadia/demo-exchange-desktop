from __future__ import annotations

import asyncio
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5 import uic

from presenters.dashboard_presenter import DashboardPresenter


class DashboardView(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("ui/dashboard.ui", self)
        self._presenter = DashboardPresenter(self)
        self._setup_tables()
        self._wire()
        self._start_refresh_timer()

    def _setup_tables(self) -> None:
        for table in (self.gainersTable, self.losersTable):
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)

    def _wire(self) -> None:
        self.logoutButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.handle_logout())
        )
        self.navPortfolio.clicked.connect(self._presenter.navigate_to_portfolio)
        self.navTrade.clicked.connect(self._presenter.navigate_to_trade)
        self.navHistory.clicked.connect(self._presenter.navigate_to_history)
        self.navWatchlist.clicked.connect(self._presenter.navigate_to_watchlist)
        self.navSearch.clicked.connect(self._presenter.navigate_to_search)

    def _start_refresh_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(
            lambda: asyncio.ensure_future(self._presenter.refresh_data())
        )
        self._timer.start(30_000)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        asyncio.ensure_future(self._presenter.refresh_data())

    # ── Presenter API ──────────────────────────────────────────

    def set_user_email(self, email: str) -> None:
        self.sidebarUserLabel.setText(email)

    def set_account_value(self, value: float, gain_loss: float, gain_loss_pct: float) -> None:
        self.accountValueAmount.setText(f"${value:,.2f}")

        sign = "+" if gain_loss >= 0 else ""
        self.pnlAmount.setText(f"{sign}${gain_loss:,.2f}")
        self.pnlPctAmount.setText(f"{sign}{gain_loss_pct:.2f}%")

        up_name = "priceUp" if gain_loss >= 0 else "priceDown"
        self.pnlAmount.setObjectName(up_name)
        self.pnlPctAmount.setObjectName(up_name)
        self.pnlAmount.style().unpolish(self.pnlAmount)
        self.pnlAmount.style().polish(self.pnlAmount)
        self.pnlPctAmount.style().unpolish(self.pnlPctAmount)
        self.pnlPctAmount.style().polish(self.pnlPctAmount)

    def set_market_status(self, is_open: bool, message: str) -> None:
        self.marketStatusLabel.setText(message)
        badge = "badgeOpen" if is_open else "badgeClosed"
        self.marketStatusLabel.setObjectName(badge)
        self.marketStatusLabel.style().unpolish(self.marketStatusLabel)
        self.marketStatusLabel.style().polish(self.marketStatusLabel)

    def set_movers(self, gainers: list[dict], losers: list[dict]) -> None:
        self._populate_movers_table(self.gainersTable, gainers, is_gainers=True)
        self._populate_movers_table(self.losersTable, losers, is_gainers=False)

    def _populate_movers_table(self, table, movers: list[dict], is_gainers: bool) -> None:
        table.setSortingEnabled(False)
        table.setRowCount(len(movers))
        color = QColor("#16a34a") if is_gainers else QColor("#dc2626")

        for row, m in enumerate(movers):
            symbol_item = QTableWidgetItem(m["symbol"])
            symbol_item.setFont(self._mono_font())

            price_item = QTableWidgetItem(f"${m['price']:,.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_item.setFont(self._mono_font())

            sign = "+" if m["percent_change"] >= 0 else ""
            change_item = QTableWidgetItem(f"{sign}{m['percent_change']:.2f}%")
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            change_item.setForeground(color)
            change_item.setFont(self._mono_font())

            table.setItem(row, 0, symbol_item)
            table.setItem(row, 1, price_item)
            table.setItem(row, 2, change_item)

        table.setSortingEnabled(True)

    def _mono_font(self):
        from PyQt5.QtGui import QFont
        f = QFont("Consolas")
        f.setPointSize(13)
        return f

    def show_loading(self, loading: bool) -> None:
        if loading:
            self.accountValueAmount.setText("Loading…")
            self.pnlAmount.setText("—")
            self.pnlPctAmount.setText("—")
            self.marketStatusLabel.setText("Loading…")

    def navigate_to_login(self) -> None:
        from views.login_view import LoginView
        self._login = LoginView()
        self._login.show()
        self.close()
