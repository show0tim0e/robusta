from textual.app import App

from vl_scanner.core import Scanner
from vl_scanner.ui.screens import AttackProgressScreen, AttackSelectorScreen, DatasetSelectorScreen, EvaluationScreen, ModelSelectorScreen, ScanConfigScreen


class VLScannerApp(App):
    SCREENS = {
        #"ModelSelectorScreen": ModelSelectorScreen,
        #"DatasetSelectorScreen": DatasetSelectorScreen,
        #"AttackSelectorScreen": AttackSelectorScreen,
        #"AttackProgressScreen": AttackProgressScreen,
        #"EvaluationScreen": EvaluationScreen,
        "ScanConfigScreen": ScanConfigScreen
    }

    scanner = Scanner()

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        self.push_screen("ScanConfigScreen")
