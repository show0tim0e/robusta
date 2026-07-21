from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static


class LaunchTab(Vertical):
    DEFAULT_CSS = """
    LaunchTab {
        height: 100%;
        padding: 2 4;
        align: center middle
    }

    #cond-vertical {
        width: 50;
        height: auto;
        border: round $accent;
        padding: 1 2;
    }

    .condition {
        width: 100%;
        height: 1;
        text-align: center;
        margin-bottom: 1;
    }

    .condition.met {
        color: $success;
        text-style: bold;
    }

    .condition.unmet {
        color: $error;
    }

    #launch-btn {
        width: 100%;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="cond-vertical"):
            yield Static("✗ Model loaded", id="cond-model", classes="condition unmet")
            yield Static("✗ Dataset loaded", id="cond-dataset", classes="condition unmet")
            yield Static("✗ At least one attack", id="cond-attacks", classes="condition unmet")
            yield Button("Launch Scanner", id="launch-btn", variant="primary", disabled=True)

    def on_mount(self) -> None:
        self.refresh_status()

    def refresh_status(self) -> None:
        scanner = self.app.scanner

        has_model = scanner.model is not None
        has_dataset = scanner.dataset is not None
        has_attacks = len(scanner.attacks) > 0

        self._update_condition("#cond-model", has_model, "Model loaded")
        self._update_condition("#cond-dataset", has_dataset, "Dataset loaded")
        self._update_condition("#cond-attacks", has_attacks, "At least one attack")

        launch_btn = self.query_one("#launch-btn", Button)
        launch_btn.disabled = not (has_model and has_dataset and has_attacks)

    def _update_condition(self, selector: str, met: bool, label: str) -> None:
        cond = self.query_one(selector, Static)
        mark = "✓" if met else "✗"
        cond.update(f"{mark} {label}")
        cond.set_class(met, "met")
        cond.set_class(not met, "unmet")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "launch-btn":
            await self._launch()

    async def _launch(self) -> None:
        from robusta.ui.screens.attack_progress import AttackProgressScreen
        self.app.push_screen(AttackProgressScreen(self.app.scanner))
