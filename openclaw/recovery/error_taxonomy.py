from __future__ import annotations

ERROR_CLASSES = {
    "auth": "rotate_or_abort",
    "billing": "switch_provider_or_block",
    "rate_limit": "backoff",
    "timeout": "retry_or_lighten_context",
    "context_overflow": "compress_context",
    "payload_too_large": "reduce_payload",
    "model_not_found": "fallback_model",
    "permission_denied": "policy_block",
    "destructive_action": "human_authorization_required",
    "unknown": "diagnose",
}

def classify_error(message: str) -> dict:
    lower = message.lower()
    for key in ERROR_CLASSES:
        if key.replace("_", " ") in lower or key in lower:
            return {"class": key, "recovery": ERROR_CLASSES[key]}
    if "402" in lower or "credit" in lower:
        return {"class": "billing", "recovery": ERROR_CLASSES["billing"]}
    if "429" in lower:
        return {"class": "rate_limit", "recovery": ERROR_CLASSES["rate_limit"]}
    return {"class": "unknown", "recovery": ERROR_CLASSES["unknown"]}
