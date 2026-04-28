from __future__ import annotations

import asyncio
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

from presenters.watchlist_presenter import WatchlistPresenter

_MONO = QFont("Consolas")
_MONO.setPointSize(13)


class WatchlistView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("ui/watchlist.ui", self)
        self._presenter = WatchlistPresenter(self)
        self._setup_table()
        self._wire()

    def _setup_table(self) -> None:
        h = self.watchlistTable.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        self.watchlistTable.verticalHeader().setVisible(False)
        self.watchlistTable.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def _wire(self) -> None:
        self.addButton.clicked.connect(self._on_add)
        self.symbolInput.returnPressed.connect(self._on_add)
        self.removeButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.remove_selected())
        )

    def _on_add(self) -> None:
        symbol = self.symbolInput.text().strip().upper()
        if symbol:
            asyncio.ensure_future(self._presenter.add_symbol(symbol))

    def _on_selection_changed(self) -> None:
        self.removeButton.setEnabled(bool(self.watchlistTable.selectedItems()))

    def on_activated(self) -> None:
        asyncio.ensure_future(self._presenter.load())

    # ── Presenter API ──────────────────────────────────────────

    def get_selected_symbol(self) -> str | None:
        row = self.watchlistTable.currentRow()
        if row < 0:
            return None
        item = self.watchlistTable.item(row, 0)
        return item.text() if item else None

    def set_rows(self, rows: list[dict]) -> None:
        self.watchlistTable.setRowCount(len(rows))
        for r, data in enumerate(rows):
            change_pct = data.get("percent_change", 0.0)
            change = data.get("change", 0.0)
            color = QColor("#16a34a") if change_pct >= 0 else QColor("#dc2626")
            sign = "+" if change_pct >= 0 else ""

            cols = [
                (data.get("symbol", ""), Qt.AlignLeft, True, None),
                (f"${data.get('close', 0):,.2f}", Qt.AlignRight, True, None),
                (f"{sign}${change:.2f}", Qt.AlignRight, True, color),
                (f"{sign}{change_pct:.2f}%", Qt.AlignRight, True, color),
            ]
            for col, (text, align, mono, fg) in enumerate(cols):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if mono:
                    item.setFont(_MONO)
                if fg:
                    item.setForeground(fg)
                self.watchlistTable.setItem(r, col, item)

    def set_add_result(self, success: bool, message: str) -> None:
        self.addResultLabel.setText(message)
        self.addResultLabel.setObjectName("successLabel" if success else "errorLabel")
        self.addResultLabel.style().unpolish(self.addResultLabel)
        self.addResultLabel.style().polish(self.addResultLabel)
        if success:
            self.symbolInput.clear()

    def set_loading(self, loading: bool) -> None:
        self.addButton.setEnabled(not loading)
        if loading:
            self.watchlistTable.setRowCount(0)
