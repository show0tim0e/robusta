from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Static


class PageCounter(Widget):
    """A widget to display progress through the app's screens as dots, with back/next navigation buttons."""

    DEFAULT_CSS = """
    PageCounter {
        layout: horizontal;
        width: 100%;
        height: 3;
    }

    #back-button {
        margin-left: 4;
    }

    #dots-indicator {
        content-align: center middle;
        width: 1fr;
        text-align: center;
        color: $text;
        text-style: bold;
    }

    #next-button {
        margin-right: 4;
    }
    """

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

    def compose(self) -> ComposeResult:
        yield Button("< Back", id="back-button")
        yield Static("", id="dots-indicator")
        yield Button("Next >", id="next-button")

    def on_mount(self) -> None:
        try:
            current_screen_name = self.screen.__class__.__name__
        except Exception:
            current_screen_name = self.app.screen.__class__.__name__

        try:
            current_index = self.screen_order.index(current_screen_name)
        except ValueError:
            current_index = -1

        back_disabled = current_index <= 0
        next_disabled = current_index < 0 or current_index >= len(self.screen_order) - 1 or current_screen_name == "AttackProgressScreen"

        self.query_one("#back-button", Button).disabled = back_disabled
        self.query_one("#next-button", Button).disabled = next_disabled

        dots = []
        for i in range(len(self.screen_order)):
            if i == current_index:
                dots.append("●")
            else:
                dots.append("○")
        dots_text = " ".join(dots)
        self.query_one("#dots-indicator", Static).update(dots_text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-button":
            self.action_back()
        elif event.button.id == "next-button":
            self.action_next()

    def action_back(self) -> None:
        screen = self.screen
        if hasattr(screen, "action_back"):
            screen.action_back()
            return

        current_screen_name = screen.__class__.__name__
        try:
            current_index = self.screen_order.index(current_screen_name)
            if current_index > 0:
                prev_screen = self.screen_order[current_index - 1]
                stack = self.app.screen_stack
                if len(stack) > 1 and stack[-2].__class__.__name__ == prev_screen:
                    self.app.pop_screen()
                else:
                    self.app.switch_screen(prev_screen)
        except ValueError:
            pass

    def action_next(self) -> None:
        screen = self.screen
        if hasattr(screen, "action_next"):
            screen.action_next()
            return

        current_screen_name = screen.__class__.__name__
        try:
            current_index = self.screen_order.index(current_screen_name)
            if current_index < len(self.screen_order) - 1:
                next_screen = self.screen_order[current_index + 1]
                self.app.push_screen(next_screen)
        except ValueError:
            pass

