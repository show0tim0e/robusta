from textual.app import RenderResult
from textual.widgets import Static


class PageCounter(Static):
    """A widget to display progress through the app's screens as dots."""

    def __init__(
        self,
        screen_order: list[str],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.screen_order = screen_order

    def render(self) -> RenderResult:
        current_screen_name = self.app.screen.__class__.__name__

        dots = []
        for name in self.screen_order:
            if name == current_screen_name:
                dots.append("●")
            else:
                dots.append("○")

        return " ".join(dots)
