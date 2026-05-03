from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

from async_utils import schedule
from main import resource_path
from presenters.dashboard_presenter import DashboardPresenter

_MONO = QFont("Consolas")
_MONO.setPointSize(13)
_REFRESH_INTERVAL_MS = 30_000


class DashboardView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(resource_path("ui/dashboard.ui"), self)
        self._presenter = DashboardPresenter(self)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(_REFRESH_INTERVAL_MS)
        self._refresh_timer.timeout.connect(
            lambda: schedule(self._presenter.refresh_data())
        )
        self._setup_tables()

    def _setup_tables(self) -> None:
        for table in (self.gainersTable, self.losersTable):
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)

    def on_activated(self) -> None:
        schedule(self._presenter.refresh_data())
        self._refresh_timer.start()

    def on_deactivated(self) -> None:
        self._refresh_timer.stop()

    # ── Presenter API ──────────────────────────────────────────

    def set_account_value(self, value: float, gain_loss: float, gain_loss_pct: float) -> None:
        self.accountValueAmount.setText(f"${value:,.2f}")
        sign = "+" if gain_loss >= 0 else ""
        self.pnlAmount.setText(f"{sign}${gain_loss:,.2f}")
        self.pnlPctAmount.setText(f"{sign}{gain_loss_pct:.2f}%")
        name = "priceUp" if gain_loss >= 0 else "priceDown"
        for lbl in (self.pnlAmount, self.pnlPctAmount):
            lbl.setObjectName(name)
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def set_market_status(self, is_open: bool, label: str) -> None:
        self.marketStatusLabel.setText(label)
        badge = "badgeOpen" if is_open else "badgeClosed"
        self.marketStatusLabel.setObjectName(badge)
        self.marketStatusLabel.style().unpolish(self.marketStatusLabel)
        self.marketStatusLabel.style().polish(self.marketStatusLabel)

    def set_movers(self, gainers: list[dict], losers: list[dict]) -> None:
        self._fill_table(self.gainersTable, gainers, is_gainers=True)
        self._fill_table(self.losersTable, losers, is_gainers=False)

    def _fill_table(self, table, movers: list[dict], is_gainers: bool) -> None:
        table.setSortingEnabled(False)
        table.setRowCount(len(movers))
        color = QColor("#16a34a") if is_gainers else QColor("#dc2626")
        for row, m in enumerate(movers):
            sign = "+" if m["percent_change"] >= 0 else ""
            items = [
                (m["symbol"], Qt.AlignLeft, None),
                (f"${m['price']:,.2f}", Qt.AlignRight, None),
                (f"{sign}{m['percent_change']:.2f}%", Qt.AlignRight, color),
            ]
            for col, (text, align, fg) in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                item.setFont(_MONO)
                if fg:
                    item.setForeground(fg)
                table.setItem(row, col, item)
        table.setSortingEnabled(True)

    def show_error(self, message: str) -> None:
        self.accountValueAmount.setText(message)

    def show_loading(self, loading: bool) -> None:
        if loading:
            self.accountValueAmount.setText("Loading…")
            self.pnlAmount.setText("—")
            self.pnlPctAmount.setText("—")
            self.marketStatusLabel.setText("Loading…")
