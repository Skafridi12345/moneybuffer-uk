"""Optional lightweight ML scam classifier.

This module provides an experimental TF-IDF + LogisticRegression signal. It is
intended to sit beside the transparent rule-based checker, not replace it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from moneybuffer.data_generation.scam_messages import generate_scam_messages

SCAM_LABEL = "scam"
LEGITIMATE_LABEL = "legitimate"

CATEGORY_MAP = {
    "bank impersonation": "bank impersonation",
    "bank impersonation scam": "bank impersonation scam",
    "HMRC refund": "HMRC scam",
    "HMRC/tax refund scam": "HMRC/tax refund scam",
    "delivery scam": "delivery scam",
    "marketplace purchase scam": "marketplace scam",
    "romance scam": "romance scam",
    "crypto investment scam": "investment scam",
    "pig-butchering crypto investment scam": "pig-butchering crypto investment scam",
    "family emergency scam": "family emergency",
    "job/task scam": "job/task scam",
    "fake recruitment or task scam": "fake recruitment or task scam",
    "authorised push payment impersonation scam": (
        "authorised push payment impersonation scam"
    ),
    "invoice redirection scam": "invoice redirection",
}


@dataclass(frozen=True)
class ScamMLModel:
    """Container for trained experimental scam classifiers."""

    binary_model: Pipeline
    category_model: Pipeline | None
    evaluation: dict[str, Any]


def load_scam_training_data(
    csv_path: str | Path = "data/synthetic/scam_messages.csv",
) -> pd.DataFrame:
    """Load synthetic scam messages, generating the CSV if it is missing."""

    path = Path(csv_path)
    if path.exists():
        data = pd.read_csv(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = generate_scam_messages()
        data.to_csv(path, index=False)

    return prepare_scam_training_data(data)


def prepare_scam_training_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalise synthetic scam-message data for model training."""

    required_columns = {"message_type", "is_scam", "message"}
    missing = required_columns.difference(data.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required scam training columns: {missing_columns}")

    prepared = data.copy()
    prepared["label"] = prepared["is_scam"].map(
        {True: SCAM_LABEL, False: LEGITIMATE_LABEL}
    )
    prepared["scam_category"] = (
        prepared["message_type"].map(CATEGORY_MAP).fillna(LEGITIMATE_LABEL)
    )
    return prepared


def _build_binary_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


def _build_category_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            (
                "classifier",
                LogisticRegression(max_iter=1000, random_state=42),
            ),
        ]
    )


def evaluate_scam_classifier(data: pd.DataFrame, seed: int = 42) -> dict[str, Any]:
    """Evaluate the binary scam classifier on synthetic data."""

    prepared = prepare_scam_training_data(data)
    label_counts = prepared["label"].value_counts()
    stratify = prepared["label"] if label_counts.min() >= 2 else None
    train, test = train_test_split(
        prepared,
        test_size=0.35,
        random_state=seed,
        stratify=stratify,
    )

    model = _build_binary_pipeline()
    model.fit(train["message"], train["label"])
    predictions = model.predict(test["message"])

    labels = [LEGITIMATE_LABEL, SCAM_LABEL]
    return {
        "accuracy": float(accuracy_score(test["label"], predictions)),
        "precision": float(
            precision_score(
                test["label"],
                predictions,
                pos_label=SCAM_LABEL,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                test["label"],
                predictions,
                pos_label=SCAM_LABEL,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                test["label"],
                predictions,
                pos_label=SCAM_LABEL,
                zero_division=0,
            )
        ),
        "confusion_matrix": confusion_matrix(
            test["label"],
            predictions,
            labels=labels,
        ).tolist(),
        "labels": labels,
        "test_size": int(len(test)),
    }


def train_scam_classifier(
    data: pd.DataFrame | None = None,
    seed: int = 42,
) -> ScamMLModel:
    """Train experimental binary and category scam classifiers."""

    prepared = (
        load_scam_training_data() if data is None else prepare_scam_training_data(data)
    )

    binary_model = _build_binary_pipeline()
    binary_model.fit(prepared["message"], prepared["label"])

    scam_rows = prepared.loc[prepared["label"] == SCAM_LABEL]
    category_model: Pipeline | None = None
    if scam_rows["scam_category"].nunique() >= 2:
        category_model = _build_category_pipeline()
        category_model.fit(scam_rows["message"], scam_rows["scam_category"])

    return ScamMLModel(
        binary_model=binary_model,
        category_model=category_model,
        evaluation=evaluate_scam_classifier(prepared, seed=seed),
    )


def predict_scam_ml(message: str, model: ScamMLModel) -> dict[str, Any]:
    """Return experimental ML scam probability and category signal."""

    probabilities = model.binary_model.predict_proba([message])[0]
    class_index = list(model.binary_model.classes_).index(SCAM_LABEL)
    scam_probability = float(probabilities[class_index])
    label = SCAM_LABEL if scam_probability >= 0.5 else LEGITIMATE_LABEL

    category = LEGITIMATE_LABEL
    if label == SCAM_LABEL and model.category_model is not None:
        category = str(model.category_model.predict([message])[0])

    return {
        "label": label,
        "scam_probability": scam_probability,
        "scam_category": category,
        "is_experimental": True,
    }
