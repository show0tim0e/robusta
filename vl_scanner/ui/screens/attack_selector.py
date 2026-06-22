from typing import Literal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import ContentSwitcher, Input, Label, SelectionList

from vl_scanner.attacks import ATTACK_REGISTRY

from .base import BaseScreen


class AttackSelectorScreen(BaseScreen):
    """Screen for selecting adversarial attacks and configuring their parameters."""

    BINDINGS = [
        Binding("p", "toggle_parameters", "Toggle Parameters", show=True),
        Binding("enter", "start_attacks", "Start Attacks", show=True),
    ]

    DEFAULT_CSS = """
    #attack-selector-container {
        layout: horizontal;
        margin: 2 4;
        height: 100%;
    }

    #attack-selector-box {
        width: 40%;
        border: round $primary;
        background: $surface;
        padding: 1 2;
    }

    #description-box {
        width: 60%;
        border: round $secondary;
        background: $surface;
        margin-left: 1;
        padding: 1 2;
    }

    #list-view {
        height: 1fr;
    }

    #attack-description {
        width: 100%;
    }

    #parameter-form {
        height: 1fr;
    }

    .parameter-row {
        height: auto;
        margin-bottom: 1;
    }

    .parameter-row Input {
        border: round $primary;
    }
    """

    def on_mount(self) -> None:
        """Set the initial state on mount."""
        self.query_one("#attack-selector-box").border_title = "Select Attacks"
        self.query_one("#description-box").border_title = "Description"
        
        list_widget = self.query_one("#list-view", SelectionList)
        list_widget.focus()
        
        # Set initial description for the first item
        if list_widget.option_count > 0:
            first_attack = list_widget.get_option_at_index(0).value
            self.query_one("#attack-description", Label).update(first_attack.description())

    def compose(self) -> ComposeResult:
        yield from super().compose()
        with Horizontal(id="attack-selector-container"):
            with Container(id="attack-selector-box"):
                with ContentSwitcher(initial="list-view"):
                    # View 1: The Attack List
                    yield SelectionList(
                        *[(attack.name(), attack) for attack in ATTACK_REGISTRY.values()],
                        id="list-view"
                    )

                    # View 2: The Parameter Form
                    with VerticalScroll(id="parameter-view"):
                        yield Vertical(id="parameter-form-container")

            with VerticalScroll(id="description-box", can_focus=False):
                yield Label("Select an attack to see its description.", id="attack-description")

    def on_selection_list_selection_highlighted(self, event: SelectionList.SelectionHighlighted) -> None:
        """Update the description box when the highlight changes."""
        attack_class = event.selection_list.get_option_at_index(event.selection_index).value
        description = attack_class.description()
        self.query_one("#attack-description", Label).update(description)

    def action_start_attacks(self) -> None:
        """Proceed to the AttackProgressScreen if at least one attack is selected."""
        list_widget = self.query_one("#list-view", SelectionList)
        selected_attacks = list_widget.selected
        
        if selected_attacks:
            self.app.push_screen("AttackProgressScreen")
        else:
            self.notify("Please select at least one attack to proceed.", severity="error")

    def action_next(self) -> None:
        """Handle Next button navigation by starting the attacks."""
        self.action_start_attacks()

    def action_toggle_parameters(self) -> None:
        """Switch to the parameter form for the highlighted attack."""
        switcher = self.query_one(ContentSwitcher)
        if switcher.current == "list-view":
            list_widget = self.query_one("#list-view", SelectionList)
            if list_widget.highlighted is not None:
                option = list_widget.get_option_at_index(list_widget.highlighted)
                attack_class = option.value
                self._build_parameter_form(attack_class)
                switcher.current = "parameter-view"
                self.query_one("#attack-selector-box").border_title = f"Parameters: {attack_class.name()}"
        else:
            self._switch_to_list()

    def _build_parameter_form(self, attack_class) -> None:
        """Dynamically build the form for the selected attack's parameters."""
        container = self.query_one("#parameter-form-container", Vertical)
        container.query("*").remove()
        
        params = attack_class.attack_parameters()
        for param in params:
            input_type: Literal["integer", "number", "text"]
            if param.type is float:
                input_type = "number"
            elif param.type is int:
                input_type = "integer"
            else:
                input_type = "text"

            inp = Input(
                placeholder=str(param.default),
                id=f"param-{param.name}",
                type=input_type
            )
            inp.border_title = param.name
            row = Horizontal(inp, classes="parameter-row")
            container.mount(row)

    def _switch_to_list(self) -> None:
        """Switch back to the attack list view."""
        switcher = self.query_one(ContentSwitcher)
        switcher.current = "list-view"
        self.query_one("#attack-selector-box").border_title = "Select Attacks"
        self.query_one("#list-view").focus()
