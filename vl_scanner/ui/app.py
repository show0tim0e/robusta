from textual.app import App

from vl_scanner.ui.screens import AttackProgressScreen, AttackSelectorScreen, DatasetSelectorScreen, EvaluationScreen, ModelSelectorScreen


class VLScannerApp(App):
    SCREENS = {
        "ModelSelectorScreen": ModelSelectorScreen,
        "DatasetSelectorScreen": DatasetSelectorScreen,
        "AttackSelectorScreen": AttackSelectorScreen,
        "AttackProgressScreen": AttackProgressScreen,
        "EvaluationScreen": EvaluationScreen,
    }

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        self.push_screen("ModelSelectorScreen")
