import huggingface_hub
from textual.app import App

from vl_scanner.core import Scanner
from vl_scanner.ui.screens import AttackProgressScreen, ScanConfigScreen


class VLScannerApp(App):
    SCREENS = {
        "AttackProgressScreen": AttackProgressScreen,
        "ScanConfigScreen": ScanConfigScreen
    }

    scanner = Scanner()

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        # Restore the HF token persisted by huggingface_hub.login() to
        # ~/.cache/huggingface/token, or from the HF_TOKEN env var. This
        # avoids asking the user to re-paste it on every launch and keeps
        # the token-button label in sync with the actual login state.
        cached = huggingface_hub.get_token()
        if cached:
            self.scanner.token = cached
        self.push_screen("ScanConfigScreen")
