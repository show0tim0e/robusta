from textual.app import ComposeResult
from .base import BaseScreen


class AttackSelectorScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield from super().compose()
