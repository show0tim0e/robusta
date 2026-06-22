from textual.app import ComposeResult

from .base import BaseScreen


class EvaluationScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield from super().compose()

    def action_back(self) -> None:
        """Go back directly to AttackSelectorScreen, bypassing the progress screen."""
        self.app.pop_screen()
