"""Content Workflow — ขั้นตอนสร้างคอนเทนต์"""

from ..channels.channel_isolation import route_product, get_channel_module
from ..content.script_builder import build_script
from ..content.claim_guard import check_claims
from ..content.content_identity import create_content_record


def run_content_pipeline(product, channel_id, angle=None):
    steps = []

    can_accept, msg = route_product(product, channel_id)
    steps.append({"step": "route", "accepted": can_accept, "message": msg})
    if not can_accept:
        return {"completed": False, "steps": steps}

    module = get_channel_module(channel_id)
    guidelines = module.script_guidelines()
    script = build_script(product, guidelines)
    steps.append({"step": "script_build", "script": script})

    script_text = script["sections"]["body"]
    claim_ok, claim_msg = check_claims(script_text)
    steps.append({"step": "claim_guard", "passed": claim_ok, "message": claim_msg})

    record = create_content_record(channel_id, product.get("id", ""), angle, script)
    steps.append({"step": "content_created", "content": record})

    return {"completed": True, "steps": steps, "content": record}
