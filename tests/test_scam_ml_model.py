from moneybuffer.data_generation.scam_messages import generate_scam_messages
from moneybuffer.scams.classifier import calculate_scam_risk_score
from moneybuffer.scams.ml_model import (
    load_scam_training_data,
    predict_scam_ml,
    train_scam_classifier,
)


def test_model_training_runs_on_synthetic_data() -> None:
    data = generate_scam_messages()
    model = train_scam_classifier(data)

    assert model.binary_model is not None
    assert model.evaluation["test_size"] > 0
    assert {"accuracy", "precision", "recall", "f1", "confusion_matrix"}.issubset(
        model.evaluation
    )


def test_prediction_returns_probability_between_zero_and_one() -> None:
    model = train_scam_classifier(generate_scam_messages())
    prediction = predict_scam_ml(
        "Urgent bank warning: verify your account using this secure link today.",
        model,
    )

    assert 0 <= prediction["scam_probability"] <= 1
    assert prediction["label"] in {"scam", "legitimate"}
    assert prediction["is_experimental"] is True


def test_rule_based_result_is_returned_without_ml_dependency(monkeypatch) -> None:
    def unavailable_classifier(*args, **kwargs):
        raise RuntimeError("optional ML unavailable")

    monkeypatch.setattr(
        "moneybuffer.scams.ml_model.train_scam_classifier",
        unavailable_classifier,
    )

    result = calculate_scam_risk_score(
        "Urgent bank warning: act now and send a bank transfer."
    )

    assert result["risk_score"] > 0
    assert result["risk_band"] in {"Medium", "High", "Severe"}
    assert result["red_flags"]


def test_scam_training_data_regenerates_when_csv_missing(tmp_path) -> None:
    missing_path = tmp_path / "missing" / "scam_messages.csv"

    data = load_scam_training_data(missing_path)

    assert missing_path.exists()
    assert {"message", "label", "scam_category"}.issubset(data.columns)
