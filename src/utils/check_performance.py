from data.models import RiskProfile
from graph.state import State


def check_performance(state: State):
    """
    Returns True if performance is satisfactory.
    For non-AGGRESSIVE profiles, requires performance_status to be True.
    For aggressive profiles, allows approval even if performance is borderline.
    """
    risk_profile = state["data"]["investment"]["user_preferences"].risk_profile
    AGGRESSIVE_PROFILES = (RiskProfile.AGGRESSIVE, RiskProfile.ULTRA_AGGRESSIVE)

    performance_status = state["data"]["analysis"]["performance"].status.value
    if risk_profile in AGGRESSIVE_PROFILES:
        return performance_status
    return True
