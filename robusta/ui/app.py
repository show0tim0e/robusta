from textual.app import App

from robusta.ui.screens import AttackProgressScreen, ScanConfigScreen


class RobustaApp(App):
    SCREENS = {
        "AttackProgressScreen": AttackProgressScreen,
        "ScanConfigScreen": ScanConfigScreen
    }

    def __init__(self) -> None:
        super().__init__()
        from robusta.core import Scanner
        self.scanner = Scanner()

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        # Restore the HF token persisted by huggingface_hub.login() to
        # ~/.cache/huggingface/token, or from the HF_TOKEN env var. This
        # avoids asking the user to re-paste it on every launch and keeps
        # the token-button label in sync with the actual login state.
        import huggingface_hub
        cached = huggingface_hub.get_token()
        if cached:
            self.scanner.token = cached
        self.push_screen("ScanConfigScreen")
