from __future__ import annotations

import asyncio
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont
from PyQt5 import uic

from presenters.trade_presenter import TradePresenter

_MONO = QFont("Consolas")
_MONO.setPointSize(13)


class TradeView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("ui/trade.ui", self)
        self._presenter = TradePresenter(self)
        self._order_type = "buy"
        self.quoteCard.setVisible(False)
        self._wire()

    def _wire(self) -> None:
        self.getQuoteButton.clicked.connect(self._on_get_quote)
        self.symbolInput.returnPressed.connect(self._on_get_quote)
        self.buyButton.clicked.connect(lambda: self._set_order_type("buy"))
        self.sellButton.clicked.connect(lambda: self._set_order_type("sell"))
        self.sharesInput.valueChanged.connect(self._update_estimated_total)
        self.placeOrderButton.clicked.connect(
            lambda: asyncio.ensure_future(self._presenter.place_order())
        )

    def _on_get_quote(self) -> None:
        symbol = self.symbolInput.text().strip().upper()
        if symbol:
            asyncio.ensure_future(self._presenter.load_quote(symbol))

    def _set_order_type(self, order_type: str) -> None:
        self._order_type = order_type
        if order_type == "buy":
            self.buyButton.setObjectName("btnBuy")
            self.sellButton.setObjectName("btnSecondary")
        else:
            self.buyButton.setObjectName("btnSecondary")
            self.sellButton.setObjectName("btnSell")
        for btn in (self.buyButton, self.sellButton):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _update_estimated_total(self) -> None:
        if self._presenter.current_price > 0:
            total = self._presenter.current_price * self.sharesInput.value()
            self.estimatedTotalLabel.setText(f"Estimated total: ${total:,.2f}")

    def on_activated(self) -> None:
        pass  # Trade page doesn't auto-refresh; user initiates lookups

    # ── Presenter API ──────────────────────────────────────────

    def get_symbol(self) -> str:
        return self.symbolInput.text().strip().upper()

    def get_shares(self) -> int:
        return self.sharesInput.value()

    def get_order_type(self) -> str:
        return self._order_type

    def set_quote(
        self,
        symbol: str,
        full_name: str,
        exchange: str,
        close: float,
        change: float,
        percent_change: float,
        open_: float,
        high: float,
        low: float,
        volume: int,
    ) -> None:
        self.quoteCard.setVisible(True)
        self.quoteNameLabel.setText(full_name)
        self.quoteExchangeLabel.setText(exchange)
        self.quotePriceLabel.setText(f"${close:,.2f}")

        sign = "+" if change >= 0 else ""
        self.quoteChangeLabel.setText(f"{sign}${change:.2f}  ({sign}{percent_change:.2f}%)")
        price_name = "priceUp" if change >= 0 else "priceDown"
        self.quoteChangeLabel.setObjectName(price_name)
        self.quoteChangeLabel.style().unpolish(self.quoteChangeLabel)
        self.quoteChangeLabel.style().polish(self.quoteChangeLabel)

        self.quoteOpenLabel.setText(f"Open: ${open_:,.2f}")
        self.quoteHighLabel.setText(f"High: ${high:,.2f}")
        self.quoteLowLabel.setText(f"Low: ${low:,.2f}")
        self.quoteVolumeLabel.setText(f"Vol: {volume:,}")

        self.placeOrderButton.setEnabled(True)
        self._update_estimated_total()

    def set_loading_quote(self, loading: bool) -> None:
        self.getQuoteButton.setEnabled(not loading)
        self.getQuoteButton.setText("Loading…" if loading else "Get Quote")

    def set_loading_order(self, loading: bool) -> None:
        self.placeOrderButton.setEnabled(not loading)
        self.placeOrderButton.setText("Placing…" if loading else "Place Order")

    def show_order_result(self, success: bool, message: str) -> None:
        self.resultLabel.setText(message)
        self.resultLabel.setObjectName("successLabel" if success else "errorLabel")
        self.resultLabel.style().unpolish(self.resultLabel)
        self.resultLabel.style().polish(self.resultLabel)

    def show_quote_error(self, message: str) -> None:
        self.quoteCard.setVisible(False)
        self.placeOrderButton.setEnabled(False)
        self.resultLabel.setText(message)
        self.resultLabel.setObjectName("errorLabel")
        self.resultLabel.style().unpolish(self.resultLabel)
        self.resultLabel.style().polish(self.resultLabel)
