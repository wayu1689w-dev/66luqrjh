"""IYO — Intelligence Yield Orchestrator — Spec sections 8-10
วิเคราะห์ข้อมูล ให้คะแนน จัดอันดับ แนะนำ
IYO Recommendation != Permission"""

from datetime import datetime, timezone
from enum import Enum

_counter = 0


class Confidence(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class ScoreState(Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    CONFLICTING = "CONFLICTING"


class Recommendation(Enum):
    SELECT_FOR_REVIEW = "SELECT_FOR_REVIEW"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEED_MORE_DATA = "NEED_MORE_DATA"
    DEFER = "DEFER"
    BLOCK = "BLOCK"


def _next_id():
    global _counter
    _counter += 1
    return f"IYO-{_counter:06d}"


def analyze(task_id, data, unknowns=None, conflicts=None, evidence_ids=None):
    """Run IYO pipeline: validate → normalize → check → score → recommend

    data: dict with fields to analyze
    unknowns: list of unknown field names
    conflicts: list of conflict dicts
    evidence_ids: list of evidence IDs supporting the data
    """
    unknowns = unknowns or []
    conflicts = conflicts or []
    evidence_ids = evidence_ids or []

    # Step 1: Validate
    validation = _validate(data)

    # Step 2: Check unknowns
    critical_unknowns = _check_unknowns(data, unknowns)

    # Step 3: Check conflicts
    open_conflicts = _check_conflicts(conflicts)

    # Step 4: Determine score state
    if open_conflicts:
        score_state = ScoreState.CONFLICTING
    elif critical_unknowns:
        score_state = ScoreState.INCOMPLETE
    else:
        score_state = ScoreState.COMPLETE

    # Step 5: Score (only if complete)
    score = _score(data) if score_state == ScoreState.COMPLETE else None

    # Step 6: Confidence
    confidence = _assess_confidence(score_state, evidence_ids, unknowns)

    # Step 7: Recommend
    recommendation = _recommend(score_state, score, confidence,
                                 critical_unknowns, open_conflicts)

    # Step 8: Action allowed?
    action_allowed = (
        recommendation in (Recommendation.SELECT_FOR_REVIEW, Recommendation.APPROVE)
        and score_state == ScoreState.COMPLETE
    )

    result_id = _next_id()

    return {
        "iyo_result_id": result_id,
        "task_id": task_id,
        "recommendation": recommendation.value,
        "score": score,
        "score_state": score_state.value,
        "confidence": confidence.value,
        "reasons": validation.get("reasons", []),
        "unknowns": critical_unknowns,
        "conflicts": [c.get("conflict_id", "?") for c in open_conflicts],
        "evidence_ids": evidence_ids,
        "action_allowed": action_allowed,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


def _validate(data):
    reasons = []
    if not data:
        reasons.append("No data provided")
    for key, val in (data or {}).items():
        if val is None:
            reasons.append(f"{key} is None")
    return {"reasons": reasons, "valid": len(reasons) == 0}


def _check_unknowns(data, unknowns):
    critical = []
    for unk in unknowns:
        if data.get(unk) is None:
            critical.append(unk)
    return critical


def _check_conflicts(conflicts):
    return [c for c in conflicts if c.get("status") == "OPEN"]


def _score(data):
    """Simple scoring based on data completeness and values.
    Real implementation would use weighted product ranking (Spec section 24)."""
    total_fields = len(data)
    filled = sum(1 for v in data.values() if v is not None and v != "UNKNOWN")
    if total_fields == 0:
        return 0.0
    return round(filled / total_fields * 100, 1)


def _assess_confidence(score_state, evidence_ids, unknowns):
    if score_state == ScoreState.CONFLICTING:
        return Confidence.LOW
    if score_state == ScoreState.INCOMPLETE:
        return Confidence.LOW if len(unknowns) > 2 else Confidence.MEDIUM
    if len(evidence_ids) >= 3:
        return Confidence.HIGH
    if len(evidence_ids) >= 1:
        return Confidence.MEDIUM
    return Confidence.UNKNOWN


def _recommend(score_state, score, confidence, unknowns, conflicts):
    if conflicts:
        return Recommendation.BLOCK
    if len(unknowns) > 2:
        return Recommendation.NEED_MORE_DATA
    if unknowns:
        return Recommendation.DEFER
    if score is not None and score >= 80 and confidence in (Confidence.HIGH, Confidence.MEDIUM):
        return Recommendation.APPROVE
    if score is not None and score >= 50:
        return Recommendation.SELECT_FOR_REVIEW
    if score is not None and score < 50:
        return Recommendation.REJECT
    return Recommendation.NEED_MORE_DATA


def reset():
    global _counter
    _counter = 0
