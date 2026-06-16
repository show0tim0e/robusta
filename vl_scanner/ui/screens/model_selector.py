from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import DirectoryTree, Input, Label

from .base import BaseScreen


class ModelSelectorScreen(BaseScreen):
    """Screen for selecting a model file or directory."""

    DEFAULT_CSS = """
    #model-selector-box {
        border: round $primary;
        background: $surface;
        margin: 2 4;
        padding: 1 2;
        height: 100%;
    }

    #model-selector-box Label {
        margin-top: 1;
        text-style: bold;
    }

    #path-input {
        border: round $primary;
    }

    #model-tree {
        margin-top: 1;
        height: 1fr;
    }
    """

    def on_mount(self) -> None:
        """Set the border title on mount."""
        self.query_one("#model-selector-box").border_title = "Select Model"

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Container(id="model-selector-box"):
            with Vertical():
                yield Label("Path:")
                yield Input(
                    placeholder="Enter path to model...",
                    id="path-input",
                    value=str(Path.cwd()),
                )
                yield DirectoryTree(Path.cwd(), id="model-tree")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when a file is selected in the DirectoryTree."""
        self.query_one("#path-input", Input).value = str(event.path)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """Called when a directory is selected in the DirectoryTree."""
        self.query_one("#path-input", Input).value = str(event.path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when the user presses enter in the path Input."""
        path = Path(event.value).expanduser().resolve()
        if path.exists():
            tree = self.query_one("#model-tree", DirectoryTree)
            if path.is_dir():
                tree.path = path
            else:
                tree.path = path.parent
        else:
            # You could add a notification here for invalid paths
            pass
