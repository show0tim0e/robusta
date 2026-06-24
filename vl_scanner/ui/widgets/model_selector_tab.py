from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Label


class ModelSelector(Vertical):
    DEFAULT_CSS = """
    ModelSelector {
        border: round $accent;
        padding: 1 2;
        margin: 1 2;
        height: auto;
    }

    ModelSelector Label {
        margin-top: 1;
    }

    ModelSelector Input {
        margin-bottom: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.border_title = "Model & Dataset"

    def compose(self) -> ComposeResult:
        yield Label("HuggingFace Model:")
        yield Input(
            placeholder="e.g., meta-llama/Llama-3-8B-Instruct",
            id="model_id",
        )

        yield Label("HuggingFace Dataset:")
        yield Input(
            placeholder="e.g., imdb",
            id="dataset_id",
        )
