from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

import asyncio
from main import resource_path
from presenters.history_presenter import HistoryPresenter

_MONO = QFont("Consolas")
_MONO.setPointSize(13)


class HistoryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(resource_path("ui/history.ui"), self)
        self._error_label = QLabel("")
        self._error_label.setObjectName("errorLabel")
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        self.layout().insertWidget(1, self._error_label)
        self._presenter = HistoryPresenter(self)
        self._setup_table()
        self._wire()

    def _setup_table(self) -> None:
        h = self.historyTable.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.Stretch)
        self.historyTable.verticalHeader().setVisible(False)

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

    def set_transactions(self, transactions: list[dict]) -> None:
        self.historyTable.setSortingEnabled(False)
        self.historyTable.setRowCount(len(transactions))
        buy_color = QColor("#16a34a")
        sell_color = QColor("#dc2626")

        for row, tx in enumerate(transactions):
            is_buy = tx.get("type", "").lower() == "buy"
            type_color = buy_color if is_buy else sell_color
            profit = tx.get("profit", 0.0)
            profit_color = QColor("#16a34a") if profit >= 0 else QColor("#dc2626")
            sign = "+" if profit >= 0 else ""

            timestamp = tx.get("time_stamp", "")
            if hasattr(timestamp, "strftime"):
                timestamp = timestamp.strftime("%Y-%m-%d  %H:%M")

            cols = [
                (tx.get("symbol", ""), Qt.AlignLeft, True, None),
                (tx.get("type", "").capitalize(), Qt.AlignLeft, False, type_color),
                (str(tx.get("amount", 0)), Qt.AlignRight, True, None),
                (f"${tx.get('price', 0):,.2f}", Qt.AlignRight, True, None),
                (f"${tx.get('value', 0):,.2f}", Qt.AlignRight, True, None),
                (f"{sign}${profit:,.2f}", Qt.AlignRight, True, profit_color),
                (str(timestamp), Qt.AlignLeft, True, None),
            ]
            for col, (text, align, mono, fg) in enumerate(cols):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if mono:
                    item.setFont(_MONO)
                if fg:
                    item.setForeground(fg)
                self.historyTable.setItem(row, col, item)

        self.historyTable.setSortingEnabled(True)

    def set_page_info(self, page: int, total_pages: int) -> None:
        self.pageLabel.setText(f"Page {page} of {total_pages}" if total_pages else "Page 1")
        self.prevButton.setEnabled(page > 1)
        self.nextButton.setEnabled(page < total_pages)

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.setVisible(bool(message))

    def set_loading(self, loading: bool) -> None:
        self.historyTable.setEnabled(not loading)
        if loading:
            self._error_label.setVisible(False)
            self.historyTable.setRowCount(0)
