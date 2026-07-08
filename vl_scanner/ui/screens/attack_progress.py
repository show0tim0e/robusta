from functools import partial

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, LoadingIndicator, ProgressBar

from vl_scanner.assessment.evaluator import Evaluator


class AttackProgressScreen(Screen):
    """Screen that runs the scanner and evaluator with progress reporting."""

    DEFAULT_CSS = """
    AttackProgressScreen {
        align: center middle;
    }

    #progress-container {
        width: 70;
        height: auto;
        align-horizontal: center;
        padding: 2;
        border: round $accent;
    }

    .phase-label {
        text-align: center;
        width: 100%;
    }

    .phase-bar {
        width: 100%;
        align-horizontal: center;
        margin-bottom: 1;
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
        self._eval_result = None

        self._worker = None
        self._eval_worker = None

        self._evaluator = Evaluator()

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="progress-container"):
            yield Label(
                "Scan: starting...",
                id="scan-label",
                classes="phase-label",
            )

            yield ProgressBar(
                total=100,
                show_eta=False,
                id="scan-bar",
                classes="phase-bar",
            )

            yield Label(
                "Evaluation: waiting for scan",
                id="eval-label",
                classes="phase-label",
            )

            yield ProgressBar(
                total=100,
                show_eta=False,
                id="eval-bar",
                classes="phase-bar",
            )

            yield LoadingIndicator(
                id="loading-indicator",
            )

        yield Footer()

    def on_mount(self) -> None:
        if len(self.scanner.attacks) == 0:
            self.query_one(
                "#scan-label",
                Label,
            ).update(
                "No attacks selected."
            )
            return

        self._worker = self.run_worker(
            self._run_scan,
            thread=True,
            exclusive=True,
        )

    ####################################################################
    # Scanner
    ####################################################################

    def _run_scan(self) -> None:
        callback = partial(
            self.app.call_from_thread,
            self._on_scan_progress,
        )

        self._result = self.scanner.run(
            progress_callback=callback,
        )

        self.app.call_from_thread(
            self._on_scan_complete,
        )

    def _on_scan_progress(
        self,
        progress: float,
        task: str,
    ) -> None:
        percent = min(progress * 100, 100)

        self.query_one(
            "#scan-bar",
            ProgressBar,
        ).update(
            progress=percent,
        )

        self.query_one(
            "#scan-label",
            Label,
        ).update(
            f"Scan: {task}"
        )

    def _on_scan_complete(self) -> None:
        self.query_one(
            "#scan-bar",
            ProgressBar,
        ).update(
            progress=100,
        )

        self.query_one(
            "#scan-label",
            Label,
        ).update(
            "Scan complete.",
        )

        self._eval_worker = self.run_worker(
            self._do_evaluate,
            thread=True,
            exclusive=True,
        )

    ####################################################################
    # Evaluator
    ####################################################################

    def _do_evaluate(self) -> None:
        callback = partial(
            self.app.call_from_thread,
            self._on_eval_progress,
        )

        if self._result is None:
            return

        self._eval_result = self._evaluator.evaluate(
            self._result,
            progress_callback=callback,
        )

        self.app.call_from_thread(
            self._on_eval_complete,
        )

    def _on_eval_progress(
        self,
        progress: float,
        task: str,
    ) -> None:
        percent = min(progress * 100, 100)

        self.query_one(
            "#eval-bar",
            ProgressBar,
        ).update(
            progress=percent,
        )

        self.query_one(
            "#eval-label",
            Label,
        ).update(
            f"Evaluation: {task}"
        )

    def _on_eval_complete(self) -> None:
        self.query_one(
            "#eval-bar",
            ProgressBar,
        ).update(
            progress=100,
        )

        self.query_one(
            "#eval-label",
            Label,
        ).update(
            "Evaluation complete.",
        )

        self.query_one(
            "#loading-indicator",
            LoadingIndicator,
        ).display = False

        self.notify(
            "Scan complete.",
            severity="information",
        )

        from vl_scanner.ui.screens.evaluation import EvaluationScreen

        self.app.push_screen(
            EvaluationScreen(
                self._eval_result or {},
            )
        )

    ####################################################################
    # Actions
    ####################################################################

    def _stop_workers(self) -> None:
        for worker in (
            self._worker,
            self._eval_worker,
        ):
            if worker is not None and not worker.is_finished:
                worker.cancel()

    def action_quit_app(self) -> None:
        self._stop_workers()
        self.app.exit()

    def action_restart(self) -> None:
        self._stop_workers()
        self.app.switch_screen("ScanConfigScreen")