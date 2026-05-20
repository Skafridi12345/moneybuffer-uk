"""Educational signposting and non-regulated recommendations."""

from moneybuffer.recommendations.action_engine import (
    DISCLAIMER,
    ActionPlan,
    generate_combined_action_plan,
    generate_cross_feature_alert,
    generate_financial_actions,
    generate_scam_actions,
)
from moneybuffer.recommendations.support_links import (
    SUPPORT_RESOURCES,
    SupportLink,
    get_relevant_support_links,
)

__all__ = [
    "ActionPlan",
    "DISCLAIMER",
    "SUPPORT_RESOURCES",
    "SupportLink",
    "generate_combined_action_plan",
    "generate_cross_feature_alert",
    "generate_financial_actions",
    "generate_scam_actions",
    "get_relevant_support_links",
]
