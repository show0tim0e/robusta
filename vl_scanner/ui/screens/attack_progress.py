from functools import partial

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, ProgressBar


class AttackProgressScreen(Screen):
    """Screen that displays a progress bar while the scanner runs selected attacks."""

    DEFAULT_CSS = """
    AttackProgressScreen {
        align: center middle;
    }

    #progress-container {
        width: 60;
        height: auto;
        align-horizontal: center;
        padding: 2;
        border: round $accent;
    }

    #progress-label {
        text-align: center;
        margin-bottom: 1;
        width: 100%;
    }

    #progress-bar {
        width: 100%;
    }
    """

    def __init__(self, scanner) -> None:
        super().__init__()
        self.scanner = scanner
        self._result = None

    def compose(self) -> ComposeResult:
        with Vertical(id="progress-container"):
            yield Label("Starting scan...", id="progress-label")
            yield ProgressBar(total=100, show_eta=True, id="progress-bar")

    def on_mount(self) -> None:
        total = len(self.scanner.attacks)
        if total == 0:
            self.query_one("#progress-label", Label).update("No attacks selected.")
            return
        self.query_one("#progress-bar", ProgressBar).update(total=total)
        self.run_worker(self._run_scan, thread=True, exclusive=True)

    def _run_scan(self) -> None:
        callback = partial(self.app.call_from_thread, self._on_progress)
        self._result = self.scanner.run(progress_callback=callback)
        self.app.call_from_thread(self._on_complete)

    def _on_progress(self, current: int, total: int, attack_name: str) -> None:
        self.query_one("#progress-bar", ProgressBar).update(progress=current)
        self.query_one("#progress-label", Label).update(
            f"Running attack {current}/{total}: {attack_name}"
        )

    def _on_complete(self) -> None:
        self.query_one("#progress-label", Label).update("Scan complete!")
        self.notify("Scan complete.", severity="information")
