"""Auto Answer — ตอบคำถามอัตโนมัติตาม pipeline"""

AUTO_ANSWER_PIPELINE = [
    "question",
    "intent",
    "required_capabilities",
    "approved_tool_discovery",
    "permission",
    "search",
    "evidence",
    "conflict_check",
    "synthesis",
    "answer",
    "citation",
    "audit",
]


def build_answer_plan(question, intent, required_tools):
    return {
        "question": question,
        "intent": intent,
        "required_tools": required_tools,
        "pipeline": AUTO_ANSWER_PIPELINE,
        "current_step": "approved_tool_discovery",
        "note": "ทุกขั้นตอนต้องผ่าน permission check",
    }
