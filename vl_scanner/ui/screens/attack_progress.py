from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import LoadingIndicator

from vl_scanner.core.providers.dataset import DatasetProvider
from vl_scanner.core.providers.model import ModelProvider
from vl_scanner.core.scanner import AttackConfig, Scanner

from .base import BaseScreen


class AttackProgressScreen(BaseScreen):
    """Screen that displays a loading indicator while the scanner runs selected attacks."""

    DEFAULT_CSS = """
    #progress-container {
        align: center middle;
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Container(id="progress-container"):
            yield LoadingIndicator()

    def action_next(self) -> None:
        """safeguard: do nothing if Next is triggered on this screen"""
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

        try:
            # 1. Load model and dataset
            model = ModelProvider.load(model_path)
            dataset = DatasetProvider.load(dataset_path)

            # 2. Build attack configurations
            configs = []
            for attack_class in selected_attacks:
                params = attack_parameters.get(attack_class, {})
                configs.append(AttackConfig(attack=attack_class, params=params))

            # 3. Initialize and run scanner
            scanner = Scanner(model=model, dataset=dataset, attacks=configs)
            results = scanner.run()

            # 4. Save results on the app
            self.app.attack_results = results

            # 5. Switch to the evaluation screen
            self.app.call_from_thread(self.app.switch_screen, "EvaluationScreen")

        except Exception as e:
            self.app.call_from_thread(
                self.notify, f"Error running attacks: {e}", severity="error"
            )
