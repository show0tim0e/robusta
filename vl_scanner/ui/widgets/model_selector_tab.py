import sys

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label

# TODO: remove dev-mode defaults in the final version

# mnist
# _DEV_MODEL_ID = "fxmarty/resnet-tiny-mnist"
# _DEV_DATASET_ID = "ylecun/mnist"
# _DEV_DATASET_SIZE = 5000

# cifar10
# _DEV_MODEL_ID = "nateraw/vit-base-patch16-224-cifar10"
# _DEV_DATASET_ID = "uoft-cs/cifar10"
# _DEV_DATASET_SIZE = 2000

# cifar100
_DEV_MODEL_ID = "Ahmed9275/Vit-Cifar100"
_DEV_DATASET_ID = "uoft-cs/cifar100"
_DEV_DATASET_SIZE = 1000


def _is_dev_mode() -> bool:
    return "--dev" in sys.argv


class ModelSelector(Vertical):
    DEFAULT_CSS = """
    ModelSelector {
        height: 1fr;
        align: center middle;
    }

    #boxes-wrapper {
        width: 100;
        height: auto;
    }

    .input-row {
        height: auto;
        layout: horizontal;
    }

    .input-row Input {
        width: 1fr;
    }

    #dataset_size {
        width: 12;
        margin-left: 1;
    }

    .input-row Button {
        width: 16;
        margin-left: 1;
    }

    .section {
        border: round $warning;
        height: 5;
        padding: 0 1;
        margin-bottom: 1;
        align: center middle;
    }

    .section.ready {
        border: round $success;
    }

    #dataset-section {
        height: auto;
    }

    .dataset-description {
        margin-top: 1;
        margin-left: 1;
        text-style: dim;
    }

    #token-container {
        height: auto;
        layout: horizontal;
    }

    #token-input {
        width: 1fr;
    }

    #token-btn {
        width: 16;
        margin-left: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._loaded_model_id = ""
        self._loaded_dataset_id = ""
        self._loaded_dataset_size: int | None = None

    def _token_button_label(self) -> str:
        scanner = getattr(self.app, "scanner", None)
        if scanner is not None and getattr(scanner, "token", None):
            return "Change Token"
        return "Save Token"

    def compose(self) -> ComposeResult:
        dev = _is_dev_mode()

        with Vertical(id="boxes-wrapper"):
            with Vertical(id="token-section", classes="section"):
                with Horizontal(id="token-container"):
                    yield Input(
                        placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                        id="token-input",
                        password=True,
                    )
                    yield Button(self._token_button_label(), id="token-btn", variant="primary")

            with Vertical(id="model-section", classes="section"):
                with Horizontal(classes="input-row"):
                    yield Input(
                        placeholder="nateraw/vit-base-patch16-224-cifar10",
                        value=_DEV_MODEL_ID if dev else "",
                        id="model_id",
                    )
                    yield Button("Load", id="model_load_btn", variant="primary")

            with Vertical(id="dataset-section", classes="section"):
                with Horizontal(classes="input-row"):
                    yield Input(
                        placeholder="uoft-cs/cifar10",
                        value=_DEV_DATASET_ID if dev else "",
                        id="dataset_id",
                    )
                    yield Input(
                        placeholder="Size",
                        value=str(_DEV_DATASET_SIZE) if dev else "",
                        id="dataset_size",
                        type="integer",
                        valid_empty=True,
                    )
                    yield Button("Load", id="dataset_load_btn", variant="primary")
                yield Label(
                    "Size: Number of images to process, leave blank for all.",
                    classes="dataset-description",
                )

    def on_mount(self) -> None:
        self.query_one("#token-section", Vertical).border_title = "HuggingFace Token"
        self.query_one("#model-section", Vertical).border_title = "HuggingFace Model"
        self.query_one("#dataset-section", Vertical).border_title = "HuggingFace Dataset & Size"
        self._update_section_states()

    def _update_section_states(self) -> None:
        scanner = getattr(self.app, "scanner", None)
        has_token = scanner is not None and bool(getattr(scanner, "token", None))
        has_model = scanner is not None and scanner.model is not None
        has_dataset = scanner is not None and scanner.dataset is not None

        token_section = self.query_one("#token-section", Vertical)
        model_section = self.query_one("#model-section", Vertical)
        dataset_section = self.query_one("#dataset-section", Vertical)

        token_section.set_class(has_token, "ready")
        model_section.set_class(has_model, "ready")
        dataset_section.set_class(has_dataset, "ready")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "token-btn":
            await self._handle_token()
        elif event.button.id == "model_load_btn":
            await self._handle_model_load()
        elif event.button.id == "dataset_load_btn":
            await self._handle_dataset_load()

    async def _handle_token(self) -> None:
        token_input = self.query_one("#token-input", Input)
        token_val = token_input.value.strip()

        if not token_val:
            self.notify("Please enter a token first.", severity="error")
            return

        self.notify("Validating Hugging Face token...")
        self.run_worker(
            lambda: self._save_token(token_val),
            thread=True,
            name="hf-save-token",
        )

    def _save_token(self, token: str) -> None:
        scanner = self.app.scanner
        success = scanner.set_token(token)

        if success:
            self.notify("Token saved. You can now load models and datasets.", severity="information")
            self.app.call_from_thread(self._on_token_saved)
        else:
            self.notify("Token validation failed.", severity="error")

    def _on_token_saved(self) -> None:
        self.query_one("#token-input", Input).value = ""
        self.query_one("#token-btn", Button).label = "Change Token"
        self._update_section_states()

    async def _handle_model_load(self) -> None:
        model_input = self.query_one("#model_id", Input)
        model_val = model_input.value.strip()

        if not model_val:
            self.notify("Please enter a model ID first.", severity="error")
            return
        if model_val == self._loaded_model_id:
            return

        scanner = self.app.scanner
        if not scanner.token:
            self.notify("Not logged in. Paste your HF token and click 'Save Token' first.", severity="error")
            return

        load_btn = self.query_one("#model_load_btn", Button)
        load_btn.label = "Loading..."
        load_btn.disabled = True

        self.notify(f"Loading model '{model_val}'...", severity="information")
        worker = self.run_worker(
            lambda: scanner.set_model(model_id=model_val),
            thread=True,
            name="load_model",
            exclusive=True,
        )
        try:
            success = await worker.wait()
        except Exception as e:
            load_btn.label = "Load"
            load_btn.disabled = False
            self.notify(f"Load crashed: {type(e).__name__}: {e}", severity="error")
            return

        if success and scanner.model is not None:
            self._loaded_model_id = model_val
            load_btn.label = "Change Model"
            load_btn.disabled = False
            self.notify(f"Model '{model_val}' loaded.", severity="information")
            self._update_section_states()
            self._refresh_launch_tab()
        else:
            load_btn.label = "Load"
            load_btn.disabled = False
            self.notify(f"Failed to load model '{model_val}'.", severity="error")

    async def _handle_dataset_load(self) -> None:
        dataset_input = self.query_one("#dataset_id", Input)
        dataset_val = dataset_input.value.strip()

        if not dataset_val:
            self.notify("Please enter a dataset ID first.", severity="error")
            return

        size_input = self.query_one("#dataset_size", Input)
        size_val = size_input.value.strip()
        size: int | None = None
        if size_val:
            try:
                size = int(size_val)
            except ValueError:
                self.notify("Dataset size must be a positive integer.", severity="error")
                return
            if size <= 0:
                self.notify("Dataset size must be a positive integer.", severity="error")
                return

        if dataset_val == self._loaded_dataset_id and size == self._loaded_dataset_size:
            return

        scanner = self.app.scanner
        if not scanner.token:
            self.notify("Not logged in. Paste your HF token and click 'Save Token' first.", severity="error")
            return

        load_btn = self.query_one("#dataset_load_btn", Button)
        load_btn.label = "Loading..."
        load_btn.disabled = True

        self.notify(f"Loading dataset '{dataset_val}'...", severity="information")
        worker = self.run_worker(
            lambda: scanner.set_dataset(dataset_id=dataset_val, size=size),
            thread=True,
            name="load_dataset",
            exclusive=True,
        )
        try:
            success = await worker.wait()
        except Exception as e:
            load_btn.label = "Load"
            load_btn.disabled = False
            self.notify(f"Load crashed: {type(e).__name__}: {e}", severity="error")
            return

        if success and scanner.dataset is not None:
            self._loaded_dataset_id = dataset_val
            self._loaded_dataset_size = size
            load_btn.label = "Change Dataset"
            load_btn.disabled = False
            self.notify(f"Dataset '{dataset_val}' loaded.", severity="information")
            self._update_section_states()
            self._refresh_launch_tab()
        else:
            load_btn.label = "Load"
            load_btn.disabled = False
            self.notify(f"Failed to load dataset '{dataset_val}'.", severity="error")

    def _refresh_launch_tab(self) -> None:
        from vl_scanner.ui.widgets.launch_tab import LaunchTab
        try:
            self.screen.query_one(LaunchTab).refresh_status()
        except Exception:
            pass
