from __future__ import annotations

import asyncio
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

from main import resource_path
from presenters.portfolio_presenter import PortfolioPresenter

_MONO = QFont("Consolas")
_MONO.setPointSize(13)


class PortfolioView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(resource_path("ui/portfolio.ui"), self)
        self._error_label = QLabel("")
        self._error_label.setObjectName("errorLabel")
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        self.layout().insertWidget(1, self._error_label)
        self._presenter = PortfolioPresenter(self)
        self._setup_table()
        self._wire()

    def _setup_table(self) -> None:
        h = self.holdingsTable.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.holdingsTable.verticalHeader().setVisible(False)

    def _wire(self) -> None:
        self.prevButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.prev_page())
        )
        self.nextButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.next_page())
        )

    def on_activated(self) -> None:
        asyncio.ensure_future(self._presenter.load_page())

    # ── Presenter API ──────────────────────────────────────────

    def set_balance(
        self,
        account_value: float,
        buying_power: float,
        total_return: float,
        total_return_pct: float,
        total_stocks: int,
    ) -> None:
        self.accountValueAmount.setText(f"${account_value:,.2f}")
        self.buyingPowerAmount.setText(f"${buying_power:,.2f}")
        self.stocksAmount.setText(str(total_stocks))
        sign = "+" if total_return >= 0 else ""
        self.totalReturnAmount.setText(
            f"{sign}${total_return:,.2f}  ({sign}{total_return_pct:.2f}%)"
        )
        name = "priceUp" if total_return >= 0 else "priceDown"
        self.totalReturnAmount.setObjectName(name)
        self.totalReturnAmount.style().unpolish(self.totalReturnAmount)
        self.totalReturnAmount.style().polish(self.totalReturnAmount)

    def set_holdings(self, holdings: list[dict]) -> None:
        self.holdingsTable.setSortingEnabled(False)
        self.holdingsTable.setRowCount(len(holdings))
        for row, h in enumerate(holdings):
            ret = h.get("total_return", 0.0)
            ret_pct = h.get("total_return_percent", 0.0)
            color = QColor("#16a34a") if ret >= 0 else QColor("#dc2626")
            sign = "+" if ret >= 0 else ""
            cols = [
                (h.get("symbol", ""), Qt.AlignLeft, True, None),
                (h.get("full_name", ""), Qt.AlignLeft, False, None),
                (str(h.get("amount", 0)), Qt.AlignRight, True, None),
                (f"${h.get('avg_price', 0):,.2f}", Qt.AlignRight, True, None),
                (f"${h.get('last_price', 0):,.2f}", Qt.AlignRight, True, None),
                (f"${h.get('total_value', 0):,.2f}", Qt.AlignRight, True, None),
                (f"{sign}${ret:,.2f}", Qt.AlignRight, True, color),
                (f"{sign}{ret_pct:.2f}%", Qt.AlignRight, True, color),
            ]
            for col, (text, align, mono, fg) in enumerate(cols):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if mono:
                    item.setFont(_MONO)
                if fg:
                    item.setForeground(fg)
                self.holdingsTable.setItem(row, col, item)
        self.holdingsTable.setSortingEnabled(True)

    def set_page_info(self, page: int, total_pages: int) -> None:
        self.pageLabel.setText(f"Page {page} of {total_pages}" if total_pages else "Page 1")
        self.prevButton.setEnabled(page > 1)
        self.nextButton.setEnabled(page < total_pages)

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.setVisible(bool(message))

    def set_loading(self, loading: bool) -> None:
        self.holdingsTable.setEnabled(not loading)
        if loading:
            self._error_label.setVisible(False)
            self.holdingsTable.setRowCount(0)
