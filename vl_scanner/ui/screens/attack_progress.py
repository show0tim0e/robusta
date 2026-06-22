from textual.app import ComposeResult

from .base import BaseScreen


class AttackProgressScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield from super().compose()
