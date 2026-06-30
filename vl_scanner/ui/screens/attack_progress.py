import sys
from functools import partial

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, LoadingIndicator, ProgressBar

# TODO: remove dev-mode sample result in the final version
_DEV_SAMPLE_RESULT = {
    "etsi_risk_level": "Critical",
    "extent_of_damage": {
        "composite_score": 3.85,
        "metrics_detail": {
            "inverted_accuracy": 0.95,
            "inverted_macro_precision": 0.98,
            "inverted_macro_recall": 0.93,
            "inverted_macro_f1": 0.99,
            "average_confidence_drop": 0.82,
        },
    },
    "attackers_effort": {
        "attack_steps": 4,
        "attack_time_seconds": 12.5,
        "computational_resources": {
            "cpu_percent": 15.2,
        },
    },
}


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
        align-horizontal: center;
    }

    #loading-indicator {
        margin-top: 1;
        height: 3;
        width: 100%;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("r", "restart", "Restart"),
    ]

    def __init__(self, scanner) -> None:
        super().__init__()
        self.scanner = scanner
        self._result = None
        self._worker = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="progress-container"):
            yield Label("Starting scan...", id="progress-label")
            yield ProgressBar(total=100, show_eta=False, id="progress-bar")
            yield LoadingIndicator(id="loading-indicator")
        yield Footer()

    def on_mount(self) -> None:
        total = len(self.scanner.attacks)
        if total == 0:
            self.query_one("#progress-label", Label).update("No attacks selected.")
            return
        self.query_one("#progress-bar", ProgressBar).update(total=total)
        self._worker = self.run_worker(self._run_scan, thread=True, exclusive=True)

    def _run_scan(self) -> None:
        callback = partial(self.app.call_from_thread, self._on_progress)
        self._result = self.scanner.run(progress_callback=callback)
        self.app.call_from_thread(self._on_complete)

    def _stop_worker(self) -> None:
        if self._worker is not None and not self._worker.is_finished:
            self._worker.cancel()

    def action_quit_app(self) -> None:
        self._stop_worker()
        self.app.exit()

    def action_restart(self) -> None:
        self._stop_worker()
        self.app.switch_screen("ScanConfigScreen")

    def _on_progress(self, current: int, total: int, attack_name: str) -> None:
        self.query_one("#progress-bar", ProgressBar).update(progress=(current - 1))
        self.query_one("#progress-label", Label).update(
            f"Running attack {current}/{total}: {attack_name}"
        )

    def _on_complete(self) -> None:
        self.query_one("#progress-label", Label).update("Scan complete!")
        self.notify("Scan complete.", severity="information")
        eval_result = self._build_eval_result()
        from vl_scanner.ui.screens.evaluation import EvaluationScreen
        self.app.push_screen(EvaluationScreen(eval_result))

    def _build_eval_result(self) -> dict:
        if "--dev" in sys.argv:
            return _DEV_SAMPLE_RESULT
        scan_result = self._result
        return {
            "etsi_risk_level": "Unknown",
            "extent_of_damage": {
                "composite_score": 0.0,
                "metrics_detail": {
                    "inverted_accuracy": 0.0,
                    "inverted_macro_precision": 0.0,
                    "inverted_macro_recall": 0.0,
                    "inverted_macro_f1": 0.0,
                    "average_confidence_drop": 0.0,
                },
            },
            "attackers_effort": {
                "attack_steps": len(scan_result.results) if scan_result is not None else 0,
                "attack_time_seconds": 0.0,
                "computational_resources": {
                    "cpu_percent": 0.0,
                },
            },
        }
