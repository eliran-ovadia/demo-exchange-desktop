from __future__ import annotations

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import uic

from views.dashboard_view import DashboardView
from views.portfolio_view import PortfolioView
from views.trade_view import TradeView
from views.history_view import HistoryView
from views.watchlist_view import WatchlistView
from views.search_view import SearchView
from async_utils import schedule
from main import resource_path, load_svg_pixmap

_NAV_BUTTONS = ["navDashboard", "navPortfolio", "navTrade",
                "navHistory", "navWatchlist", "navSearch"]


class MainWindowView(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(resource_path("ui/main_window.ui"), self)
        self._load_sidebar_logo()

        self._pages = [
            DashboardView(),
            PortfolioView(),
            TradeView(),
            HistoryView(),
            WatchlistView(),
            SearchView(),
        ]
        for page in self._pages:
            self.stackedWidget.addWidget(page)

        self._current_index = 0
        self._wire()
        self._switch(0)

    def _load_sidebar_logo(self) -> None:
        pixmap = load_svg_pixmap("assets/logo_sidebar.svg", 176, 38)
        self.sidebarLogoLabel.setPixmap(pixmap)
        self.sidebarLogoLabel.setText("")
        self.sidebarLogoLabel.setFixedSize(176, 38)
        self.sidebarLogoLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def _wire(self) -> None:
        self.navDashboard.clicked.connect(lambda: self._switch(0))
        self.navPortfolio.clicked.connect(lambda: self._switch(1))
        self.navTrade.clicked.connect(lambda: self._switch(2))
        self.navHistory.clicked.connect(lambda: self._switch(3))
        self.navWatchlist.clicked.connect(lambda: self._switch(4))
        self.navSearch.clicked.connect(lambda: self._switch(5))
        self.logoutButton.clicked.connect(
            lambda: schedule(self._handle_logout())
        )

    def _switch(self, index: int) -> None:
        outgoing = self._pages[self._current_index]
        if hasattr(outgoing, "on_deactivated"):
            outgoing.on_deactivated()
        self._current_index = index
        self.stackedWidget.setCurrentIndex(index)
        self._set_active_nav(index)
        page = self._pages[index]
        if hasattr(page, "on_activated"):
            page.on_activated()

    def _set_active_nav(self, active_index: int) -> None:
        for i, name in enumerate(_NAV_BUTTONS):
            btn = getattr(self, name)
            obj_name = "navItemActive" if i == active_index else "navItem"
            btn.setObjectName(obj_name)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    async def _handle_logout(self) -> None:
        from services.auth_service import auth_service
        await auth_service.logout()
        from views.login_view import LoginView
        self._login = LoginView()
        self._login.show()
        self.close()

    def set_user_email(self, email: str) -> None:
        self.sidebarUserLabel.setText(email)
