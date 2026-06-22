from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header

from vl_scanner.ui.widgets.page_counter import PageCounter


class BaseScreen(Screen):
    """Provides a shared layout between all the screens of the app"""

    DEFAULT_CSS = """
    PageCounter {
        dock: bottom;
        height: 3;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield PageCounter(list(self.app.SCREENS.keys()))
