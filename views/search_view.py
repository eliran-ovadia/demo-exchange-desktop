from __future__ import annotations

import asyncio
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

from presenters.search_presenter import SearchPresenter

_MONO = QFont("Consolas")
_MONO.setPointSize(13)


class SearchView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("ui/search.ui", self)
        self._presenter = SearchPresenter(self)
        self._setup_table()
        self._wire()
        self.detailPanel.setVisible(False)

        self._search_error_label = QLabel("")
        self._search_error_label.setObjectName("errorLabel")
        self._search_error_label.setWordWrap(True)
        self._search_error_label.setVisible(False)
        self.layout().insertWidget(1, self._search_error_label)

        self._watchlist_result_label = QLabel("")
        self._watchlist_result_label.setWordWrap(True)
        if self.detailPanel.layout():
            self.detailPanel.layout().addWidget(self._watchlist_result_label)

    def _setup_table(self) -> None:
        h = self.resultsTable.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.resultsTable.verticalHeader().setVisible(False)

    def _wire(self) -> None:
        self.searchButton.clicked.connect(self._on_search)
        self.searchInput.returnPressed.connect(self._on_search)
        self.resultsTable.itemSelectionChanged.connect(self._on_result_selected)
        self.addToWatchlistButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.add_to_watchlist())
        )

    def _on_search(self) -> None:
        query = self.searchInput.text().strip()
        if query:
            asyncio.ensure_future(self._presenter.search(query))

    def _on_result_selected(self) -> None:
        row = self.resultsTable.currentRow()
        if row >= 0:
            symbol_item = self.resultsTable.item(row, 0)
            if symbol_item:
                asyncio.ensure_future(
                    self._presenter.load_detail(symbol_item.text())
                )

    def on_activated(self) -> None:
        pass  # user initiates searches

    # ── Presenter API ──────────────────────────────────────────

    def set_results(self, results: list[dict]) -> None:
        self.resultsTable.setRowCount(len(results))
        for row, r in enumerate(results):
            cols = [
                (r.get("symbol", ""), Qt.AlignLeft, True),
                (r.get("instrument_name", ""), Qt.AlignLeft, False),
                (r.get("exchange", ""), Qt.AlignLeft, False),
                (r.get("country", ""), Qt.AlignLeft, False),
            ]
            for col, (text, align, mono) in enumerate(cols):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if mono:
                    item.setFont(_MONO)
                self.resultsTable.setItem(row, col, item)

    def set_detail(
        self,
        symbol: str,
        full_name: str,
        close: float,
        change: float,
        percent_change: float,
        open_: float,
        high: float,
        low: float,
    ) -> None:
        self.detailPanel.setVisible(True)
        self.detailNameLabel.setText(f"{symbol} — {full_name}")
        self.detailPriceLabel.setText(f"${close:,.2f}")

        sign = "+" if change >= 0 else ""
        self.detailChangeLabel.setText(f"{sign}${change:.2f}  ({sign}{percent_change:.2f}%)")
        price_name = "priceUp" if change >= 0 else "priceDown"
        self.detailChangeLabel.setObjectName(price_name)
        self.detailChangeLabel.style().unpolish(self.detailChangeLabel)
        self.detailChangeLabel.style().polish(self.detailChangeLabel)

        self.detailOpenLabel.setText(f"Open: ${open_:,.2f}")
        self.detailHighLabel.setText(f"High: ${high:,.2f}")
        self.detailLowLabel.setText(f"Low: ${low:,.2f}")
        self.addToWatchlistButton.setEnabled(True)

    def set_sentiment(
        self,
        strong_buy: int,
        buy: int,
        hold: int,
        sell: int,
        strong_sell: int,
        consensus: str | None,
    ) -> None:
        self.sentimentStrongBuyLabel.setText(f"Strong Buy {strong_buy}")
        self.sentimentBuyLabel.setText(f"Buy {buy}")
        self.sentimentHoldLabel.setText(f"Hold {hold}")
        self.sentimentSellLabel.setText(f"Sell {sell}")
        self.sentimentStrongSellLabel.setText(f"Strong Sell {strong_sell}")
        self.consensusBadge.setText(consensus or "—")

        badge_name = "badgeOpen" if (consensus or "").lower() in ("buy", "strong buy") \
            else "badgeClosed" if (consensus or "").lower() in ("sell", "strong sell") \
            else "badgeNeutral"
        self.consensusBadge.setObjectName(badge_name)
        self.consensusBadge.style().unpolish(self.consensusBadge)
        self.consensusBadge.style().polish(self.consensusBadge)

    def show_search_error(self, message: str) -> None:
        self._search_error_label.setText(message)
        self._search_error_label.setVisible(bool(message))

    def show_watchlist_result(self, success: bool, message: str) -> None:
        self._watchlist_result_label.setText(message)
        obj_name = "successLabel" if success else "errorLabel"
        self._watchlist_result_label.setObjectName(obj_name)
        self._watchlist_result_label.style().unpolish(self._watchlist_result_label)
        self._watchlist_result_label.style().polish(self._watchlist_result_label)

    def set_loading_search(self, loading: bool) -> None:
        self._search_error_label.setVisible(False)
        self.searchButton.setEnabled(not loading)
        self.searchButton.setText("Searching…" if loading else "Search")

    def get_selected_symbol(self) -> str | None:
        row = self.resultsTable.currentRow()
        if row < 0:
            return None
        item = self.resultsTable.item(row, 0)
        return item.text() if item else None
