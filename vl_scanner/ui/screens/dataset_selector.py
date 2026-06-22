from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import DirectoryTree, Input

from .base import BaseScreen


class DatasetSelectorScreen(BaseScreen):
    """Screen for selecting a dataset file."""

    DEFAULT_CSS = """
    #dataset-selector-box {
        border: round $primary;
        background: $surface;
        margin: 2 4;
        padding: 1 2;
        height: 100%;
    }

    #dataset-selector-box Label {
        margin-top: 1;
        text-style: bold;
    }

    #dataset-path-input {
        border: round $primary;
    }

    #dataset-tree {
        margin-top: 1;
        height: 1fr;
    }
    """

    def on_mount(self) -> None:
        """Set the border title and default focus on mount."""
        self.query_one("#dataset-selector-box").border_title = "Select Dataset"
        path_input = self.query_one("#dataset-path-input", Input)
        path_input.border_title = "Path"
        self.query_one("#dataset-tree").focus()

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Container(id="dataset-selector-box"):
            with Vertical():
                yield Input(
                    placeholder="Enter path to dataset...",
                    id="dataset-path-input",
                    value=str(Path.cwd()),
                )
                yield DirectoryTree(Path.cwd(), id="dataset-tree")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when a file is selected in the DirectoryTree."""
        self.query_one("#dataset-path-input", Input).value = str(event.path)
        self.app.dataset_path = event.path
        self.app.push_screen("AttackSelectorScreen")

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """Called when a directory is selected in the DirectoryTree."""
        self.query_one("#dataset-path-input", Input).value = str(event.path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Called when the user presses enter in the path Input."""
        path = Path(event.value).expanduser().resolve()
        if path.exists():
            tree = self.query_one("#dataset-tree", DirectoryTree)
            if path.is_dir():
                tree.path = path
            else:
                tree.path = path.parent
                self.app.dataset_path = path
                self.app.push_screen("AttackSelectorScreen")

    def action_next(self) -> None:
        """Handle Next button navigation by submitting the current path."""
        path_input = self.query_one("#dataset-path-input", Input)
        path = Path(path_input.value).expanduser().resolve()
        if path.exists():
            tree = self.query_one("#dataset-tree", DirectoryTree)
            if path.is_dir():
                tree.path = path
            else:
                tree.path = path.parent
                self.app.dataset_path = path
                self.app.push_screen("AttackSelectorScreen")
        else:
            self.notify("Invalid path. Please select a valid file or directory.", severity="error")
