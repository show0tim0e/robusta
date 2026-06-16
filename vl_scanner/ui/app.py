from textual.app import App
from textual.theme import Theme

from vl_scanner.ui.screens import ModelSelectorScreen, AttackSelectorScreen, AttackProgressScreen, EvaluationScreen

CUSTOM_LIGHT = Theme(
    name="vl-light",
    primary="#2f6a3a",
    secondary="#86d093",
    accent="#359c48",
    background="#f8fcf8",
    surface="#f8fcf8",
    foreground="#0d170e",
)

CUSTOM_DARK = Theme(
    name="vl-dark",
    primary="#95d0a0",
    secondary="#2f793d",
    accent="#63ca76",
    background="#030703",
    surface="#030703",
    foreground="#e8f2e9",
)


class VLScannerApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle Dark Mode")]

    SCREENS = {
        "ModelSelectorScreen": ModelSelectorScreen,
        "AttackSelectorScreen": AttackSelectorScreen,
        "AttackProgressScreen": AttackProgressScreen,
        "EvaluationScreen": EvaluationScreen,
    }

    # Register the themes
    def on_mount(self) -> None:
        self.register_theme(CUSTOM_LIGHT)
        self.register_theme(CUSTOM_DARK)
        self.theme = "vl-dark"
        self.push_screen("ModelSelectorScreen")

    def action_toggle_dark(self) -> None:
        """An action to toggle between dark and light themes."""
        self.theme = "vl-light" if self.theme == "vl-dark" else "vl-dark"