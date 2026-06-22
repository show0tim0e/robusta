from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import LoadingIndicator, RichLog

from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider
from vl_scanner.core.scanner import AttackConfig, Scanner
from .base import BaseScreen


class AttackProgressScreen(BaseScreen):
    """Screen that displays a loading indicator while the scanner runs selected attacks."""

    BINDINGS = [
        Binding("l", "toggle_log", "Toggle Log", show=True),
    ]

    DEFAULT_CSS = """
    #progress-container {
        align: center middle;
        height: 1fr;
    }

    #progress-log {
        display: none;
        height: 1fr;
        border: round $primary;
        background: $surface;
        margin: 1 4;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Container(id="progress-container"):
            yield LoadingIndicator()
        yield RichLog(id="progress-log", highlight=True, markup=True)

    def action_next(self) -> None:
        """safeguard: do nothing if Next is triggered on this screen"""
        pass

    def action_toggle_log(self) -> None:
        """Toggle visibility of the progress log widget."""
        log_widget = self.query_one("#progress-log", RichLog)
        log_widget.display = not log_widget.display
        if log_widget.display:
            log_widget.focus()
        else:
            self.focus()

    def log_message(self, message: str) -> None:
        """Write a message to the RichLog widget from any thread."""
        try:
            log_widget = self.query_one("#progress-log", RichLog)
            self.app.call_from_thread(log_widget.write, message)
        except Exception:
            pass

    def on_mount(self) -> None:
        """Run the attack scanner in a background worker thread when mounted."""
        self.run_worker(self._run_attacks, thread=True)

    def _run_attacks(self) -> None:
        model_path = getattr(self.app, "model_path", None)
        dataset_path = getattr(self.app, "dataset_path", None)
        selected_attacks = getattr(self.app, "selected_attacks", [])
        attack_parameters = getattr(self.app, "attack_parameters", {})

        if not model_path or not dataset_path:
            self.app.call_from_thread(
                self.notify, "Missing model or dataset path.", severity="error"
            )
            return

        self.log_message(f"Loading model from: {model_path}")
        try:
            # 1. Load model and dataset
            model = ModelProvider.load(model_path)
            self.log_message("Model loaded successfully.")

            self.log_message(f"Loading dataset from: {dataset_path}")
            dataset = DatasetProvider.load(dataset_path)
            self.log_message("Dataset loaded successfully.")

            # 2. Build attack configurations
            configs = []
            for attack_class in selected_attacks:
                params = attack_parameters.get(attack_class, {})
                configs.append(AttackConfig(attack=attack_class, params=params))

            # 3. Initialize and run scanner
            results = []
            self.log_message(f"Starting {len(configs)} adversarial attacks...")
            
            for i, config in enumerate(configs):
                self.log_message(f"[{i+1}/{len(configs)}] Running attack: {config.attack.name()} with params: {config.params}")
                single_scanner = Scanner(model=model, dataset=dataset, attacks=[config])
                single_results = single_scanner.run()
                results.extend(single_results)
                self.log_message(f"[{i+1}/{len(configs)}] Finished attack: {config.attack.name()}")

            self.log_message("Successfully completed all attacks!")

            # 4. Save results on the app
            self.app.attack_results = results

            # 5. Switch to the evaluation screen
            self.app.call_from_thread(self.app.switch_screen, "EvaluationScreen")

        except Exception as e:
            self.log_message(f"ERROR: {e}")
            self.app.call_from_thread(
                self.notify, f"Error running attacks: {e}", severity="error"
            )

