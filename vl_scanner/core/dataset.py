from dataclasses import dataclass
from pathlib import Path

from torch import Tensor


@dataclass(slots=True)
class Dataset:
    path: str

    def __post_init__(self) -> None:
        candidate = Path(self.path)
        if not candidate.is_absolute():
            raise ValueError("Dataset path must be an absolute path.")

        self.path = str(candidate)

    def as_path(self) -> Path:
        return Path(self.path)

    def load(self) -> tuple[Tensor, Tensor]:
        pass