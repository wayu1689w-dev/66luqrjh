"""Tool Classification — จำแนกประเภทเครื่องมือ"""

from enum import Enum


class ToolClass(Enum):
    SEARCH = "search"
    READ = "read"
    ANALYZE = "analyze"
    GENERATE = "generate"
    DRAFT = "draft"
    CREATE = "create"
    UPDATE = "update"
    PUBLISH = "publish"
    SEND = "send"
    DELETE = "delete"
    COMMERCE = "commerce"
    FINANCE = "finance"
    ADS = "ads"
    IDENTITY = "identity"
    ADMIN = "admin"


SAFE_CLASSES = {ToolClass.SEARCH, ToolClass.READ, ToolClass.ANALYZE}
CONTROLLED_CLASSES = {ToolClass.GENERATE, ToolClass.DRAFT}
APPROVAL_CLASSES = {ToolClass.CREATE, ToolClass.UPDATE}
EXPLICIT_APPROVAL_CLASSES = {ToolClass.PUBLISH, ToolClass.SEND, ToolClass.DELETE}
STRONGEST_APPROVAL_CLASSES = {ToolClass.COMMERCE, ToolClass.FINANCE, ToolClass.ADS, ToolClass.IDENTITY, ToolClass.ADMIN}


def classify_tool(tool_type):
    tool_type = tool_type.lower()
    for tc in ToolClass:
        if tc.value == tool_type:
            return tc
    return ToolClass.READ


def requires_approval(tool_class):
    if tool_class in SAFE_CLASSES:
        return False, "policy may auto-allow"
    if tool_class in CONTROLLED_CLASSES:
        return False, "controlled — ตรวจก่อนใช้"
    if tool_class in APPROVAL_CLASSES:
        return True, "ต้องได้รับอนุมัติ"
    if tool_class in EXPLICIT_APPROVAL_CLASSES:
        return True, "ต้องได้รับอนุมัติชัดเจน"
    if tool_class in STRONGEST_APPROVAL_CLASSES:
        return True, "ต้องได้รับอนุมัติระดับสูงสุด"
    return True, "ไม่รู้จักประเภท — ต้องอนุมัติ"
