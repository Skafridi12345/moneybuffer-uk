"""Train and evaluate the optional synthetic scam classifier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def main() -> None:
    """Train the lightweight classifier and print evaluation metrics."""

    from moneybuffer.scams.ml_model import (
        load_scam_training_data,
        train_scam_classifier,
    )

    data = load_scam_training_data(
        PROJECT_ROOT / "data" / "synthetic" / "scam_messages.csv"
    )
    model = train_scam_classifier(data)
    print(json.dumps(model.evaluation, indent=2))


if __name__ == "__main__":
    main()
