from textual.app import ComposeResult
from .base import BaseScreen


class ModelSelectorScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield from super().compose()