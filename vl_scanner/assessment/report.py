from typing import Any, Dict


class Report:
    def build(
        self,
        clean: Dict[str, float],
        attacks: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        pass