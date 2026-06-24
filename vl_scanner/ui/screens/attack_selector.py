from typing import Literal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import ContentSwitcher, Input, Label, SelectionList

from vl_scanner.attacks import Attack

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
                        *[(attack.name(), attack) for attack in Attack.registry.values()],
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
        self._save_current_parameters()
        
        list_widget = self.query_one("#list-view", SelectionList)
        selected_attacks = list_widget.selected
        
        if selected_attacks:
            # Initialize attack_parameters on app if not exists
            if not hasattr(self.app, "attack_parameters"):
                self.app.attack_parameters = {}
                
            # For any selected attack that has no parameters saved, populate with defaults
            for attack_class in selected_attacks:
                if attack_class not in self.app.attack_parameters:
                    defaults = {p.name: p.default for p in attack_class.attack_parameters()}
                    self.app.attack_parameters[attack_class] = defaults
            
            # Save selected attacks to app
            self.app.selected_attacks = selected_attacks
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

    def _save_current_parameters(self) -> None:
        """Save the parameters from the form for the currently viewed attack."""
        if not hasattr(self, "current_parameter_attack") or self.current_parameter_attack is None:
            return
            
        attack_class = self.current_parameter_attack
        params = attack_class.attack_parameters()
        
        param_values = {}
        for param in params:
            try:
                inp = self.query_one(f"#param-{param.name}", Input)
                value_str = inp.value.strip()
                if not value_str:
                    value = param.default
                else:
                    if param.type is float:
                        value = float(value_str)
                    elif param.type is int:
                        value = int(value_str)
                    else:
                        value = value_str
                param_values[param.name] = value
            except Exception:
                param_values[param.name] = param.default
                
        if not hasattr(self.app, "attack_parameters"):
            self.app.attack_parameters = {}
        self.app.attack_parameters[attack_class] = param_values

    def _build_parameter_form(self, attack_class) -> None:
        """Dynamically build the form for the selected attack's parameters."""
        self._save_current_parameters()
        self.current_parameter_attack = attack_class
        
        container = self.query_one("#parameter-form-container", Vertical)
        container.query("*").remove()
        
        saved_params = getattr(self.app, "attack_parameters", {}).get(attack_class, {})
        params = attack_class.attack_parameters()
        for param in params:
            input_type: Literal["integer", "number", "text"]
            if param.type is float:
                input_type = "number"
            elif param.type is int:
                input_type = "integer"
            else:
                input_type = "text"

            val = str(saved_params[param.name]) if param.name in saved_params else ""

            inp = Input(
                placeholder=str(param.default),
                id=f"param-{param.name}",
                type=input_type,
                value=val
            )
            inp.border_title = param.name
            row = Horizontal(inp, classes="parameter-row")
            container.mount(row)

    def _switch_to_list(self) -> None:
        """Switch back to the attack list view."""
        self._save_current_parameters()
        self.current_parameter_attack = None
        
        switcher = self.query_one(ContentSwitcher)
        switcher.current = "list-view"
        self.query_one("#attack-selector-box").border_title = "Select Attacks"
        self.query_one("#list-view").focus()
