def build_review_queue(fields: dict) -> list[dict]:
    queue = []

    for field_name, field_data in fields.items():
        reason = None


        if not field_data.get("is_found"):
            reason = "field not found in document"


        elif field_data.get("confidence") in ["low", "medium"]:
            reason = f"confidence is {field_data.get('confidence')}"


        elif field_name == "auto_renewal" and field_data.get("is_auto_renewal"):
            reason = "high risk field - always requires review"

        elif field_data.get("raw_text") is None:
            reason = "no source text found - extraction unverifiable"

        if reason:
            queue.append({
                "field_name": field_name,
                "reason": reason,
                "extracted_value": field_data.get(field_name) or str(field_data),
                "confidence": field_data.get("confidence"),
                "status": "pending"
            })

    return queue