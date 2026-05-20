"""Scam-risk exposure education and indicators."""

from moneybuffer.scams.classifier import calculate_scam_risk_score, classify_scam_type
from moneybuffer.scams.explanations import explain_scam_risk
from moneybuffer.scams.ml_model import predict_scam_ml, train_scam_classifier
from moneybuffer.scams.rules import detect_red_flags

__all__ = [
    "calculate_scam_risk_score",
    "classify_scam_type",
    "detect_red_flags",
    "explain_scam_risk",
    "predict_scam_ml",
    "train_scam_classifier",
]
