from textual.app import App

from vl_scanner.ui.screens import ModelSelectorScreen, AttackSelectorScreen, AttackProgressScreen, EvaluationScreen


class VLScannerApp(App):
    SCREENS = {
        "ModelSelectorScreen": ModelSelectorScreen,
        "AttackSelectorScreen": AttackSelectorScreen,
        "AttackProgressScreen": AttackProgressScreen,
        "EvaluationScreen": EvaluationScreen,
    }

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        self.push_screen("ModelSelectorScreen")
