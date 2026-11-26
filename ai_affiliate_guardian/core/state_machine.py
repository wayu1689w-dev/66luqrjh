"""State machine สำหรับ Product, Content, Approval, Money"""

from enum import Enum


class ProductState(Enum):
    INTAKE = "intake"
    ELIGIBLE = "eligible"
    REJECTED = "rejected"
    RANKED = "ranked"
    ASSIGNED = "assigned"
    SCRIPTED = "scripted"
    QC_PASSED = "qc_passed"
    APPROVED = "approved"
    PUBLISHED = "published"
    MEASURING = "measuring"
    ARCHIVED = "archived"


class ContentState(Enum):
    DRAFT = "draft"
    SCRIPTED = "scripted"
    MEDIA_READY = "media_ready"
    QC_PENDING = "qc_pending"
    QC_PASSED = "qc_passed"
    QC_FAILED = "qc_failed"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    PUBLISHED = "published"
    REVOKED = "revoked"


class ApprovalState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"


class MoneyState(Enum):
    UNKNOWN = "unknown"
    ESTIMATED = "estimated"
    CONFIRMED = "confirmed"
    INVOICED = "invoiced"
    PAID = "paid"
    DISPUTED = "disputed"


PRODUCT_TRANSITIONS = {
    ProductState.INTAKE: [ProductState.ELIGIBLE, ProductState.REJECTED],
    ProductState.ELIGIBLE: [ProductState.RANKED, ProductState.REJECTED],
    ProductState.RANKED: [ProductState.ASSIGNED],
    ProductState.ASSIGNED: [ProductState.SCRIPTED],
    ProductState.SCRIPTED: [ProductState.QC_PASSED, ProductState.ASSIGNED],
    ProductState.QC_PASSED: [ProductState.APPROVED],
    ProductState.APPROVED: [ProductState.PUBLISHED],
    ProductState.PUBLISHED: [ProductState.MEASURING, ProductState.ARCHIVED],
    ProductState.MEASURING: [ProductState.ARCHIVED],
}


def can_transition(current, target, transitions):
    allowed = transitions.get(current, [])
    return target in allowed


def transition(current, target, transitions):
    if not can_transition(current, target, transitions):
        raise ValueError(
            f"ไม่สามารถเปลี่ยนสถานะจาก {current.value} เป็น {target.value}"
        )
    return target
