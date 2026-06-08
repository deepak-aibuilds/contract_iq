import streamlit as st
from app.services import extract_pdf, chunk_by_sections, build_review_queue
from app.services import extract_payment, extract_termination, extract_renewal
import asyncio

st.set_page_config(page_title="ContractIQ", layout="wide")

# --- HEADER ---
st.title("ContractIQ")
st.caption("Automated first-pass contract review — powered by Mistral AI")

# --- UPLOAD SCREEN ---
uploaded_file = st.file_uploader("Upload a contract PDF", type=["pdf"])

if uploaded_file:
    if st.button("Extract Contract", type="primary"):
        with st.spinner("Reading and extracting contract..."):
            try:
                file_bytes = uploaded_file.read()

                result = extract_pdf(file_bytes)

                if not result["success"]:
                    st.error(f"Extraction failed: {result['warning']}")
                    st.stop()

                if result.get("warning"):
                    st.warning(result["warning"])

                chunks = chunk_by_sections(result["text"])

                fields = {
                    "payment_terms": asyncio.run(extract_payment(chunks)),
                    "termination": asyncio.run(extract_termination(chunks)),
                    "auto_renewal": asyncio.run(extract_renewal(chunks))
                }

                review_queue = build_review_queue(fields)

                st.session_state["fields"] = fields
                st.session_state["review_queue"] = review_queue
                st.session_state["filename"] = uploaded_file.name
                st.session_state["page_count"] = result["page_count"]
                st.session_state["char_count"] = result["char_count"]

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                st.stop()

# --- RESULTS SCREEN ---
if "fields" in st.session_state:
    fields = st.session_state["fields"]
    review_queue = st.session_state["review_queue"]

    st.divider()

    # doc metadata
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.metric("File", st.session_state["filename"])
    with meta_col2:
        st.metric("Pages", st.session_state.get("page_count", "—"))
    with meta_col3:
        flagged = len([r for r in review_queue if r["status"] == "pending"])
        st.metric("Flagged for Review", flagged)

    st.divider()
    st.subheader("Extracted Fields")

    col1, col2, col3 = st.columns(3)

    # helper to render confidence badge
    def confidence_badge(confidence: str):
        color = "green" if confidence == "high" else "orange" if confidence == "medium" else "red"
        st.markdown(f"**Confidence:** :{color}[{confidence}]")

    # helper — safely get attribute or dict value
    def get_val(obj, key):
        if obj is None:
            return "—"
        val = getattr(obj, key, None) if hasattr(obj, key) else obj.get(key)
        return val if val is not None else "—"

    with col1:
        st.markdown("### 💰 Payment Terms")
        pt = fields["payment_terms"]
        st.write("**Amount & Schedule:**", get_val(pt, "payment_terms"))
        st.write("**Notes:**", get_val(pt, "notes"))
        with st.expander("Source text"):
            st.write(get_val(pt, "raw_text"))
        confidence_badge(get_val(pt, "confidence"))

    with col2:
        st.markdown("### 🔴 Termination")
        t = fields["termination"]
        st.write("**Notice Period:**", get_val(t, "notice_period"))
        st.write("**Type:**", get_val(t, "termination_type"))
        st.write("**Condition:**", get_val(t, "condition"))
        with st.expander("Source text"):
            st.write(get_val(t, "raw_text"))
        confidence_badge(get_val(t, "confidence"))

    with col3:
        st.markdown("### 🔄 Auto-Renewal")
        ar = fields["auto_renewal"]
        is_renewal = get_val(ar, "is_auto_renewal")
        st.write("**Auto-Renewal:**", "✅ Yes" if is_renewal else "❌ No")
        st.write("**Notice Required:**", get_val(ar, "notice_required"))
        st.write("**Renewal Terms:**", get_val(ar, "renewal_terms"))
        with st.expander("Source text"):
            st.write(get_val(ar, "raw_text"))
        confidence_badge(get_val(ar, "confidence"))

    # --- REVIEW QUEUE ---
    st.divider()
    st.subheader("Review Queue")

    if not review_queue:
        st.success("✅ No items flagged for review.")
    else:
        pending = [r for r in review_queue if r["status"] == "pending"]
        confirmed = [r for r in review_queue if r["status"] == "confirmed"]
        corrected = [r for r in review_queue if r["status"] == "corrected"]

        if pending:
            st.warning(f"{len(pending)} item(s) require your review.")
        if confirmed or corrected:
            st.success(f"{len(confirmed)} confirmed, {len(corrected)} corrected.")

        for i, item in enumerate(st.session_state["review_queue"]):
            status = item["status"]
            icon = "⚠️" if status == "pending" else "✅" if status == "confirmed" else "✏️"

            with st.expander(f"{icon} {item['field_name']} — {item['reason']} [{status}]"):
                st.write("**Extracted Value:**", item.get("extracted_value") or "—")
                st.write("**Confidence:**", item.get("confidence") or "—")
                st.write("**Status:**", status)

                if item.get("corrected_value"):
                    st.info(f"Corrected to: {item['corrected_value']}")

                if status == "pending":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Confirm", key=f"confirm_{i}"):
                            st.session_state["review_queue"][i]["status"] = "confirmed"
                            st.rerun()
                    with col_b:
                        correction = st.text_input(
                            "Enter correction",
                            key=f"correct_{i}",
                            placeholder="Type corrected value..."
                        )
                        if st.button("💾 Save Correction", key=f"save_{i}"):
                            if correction.strip():
                                st.session_state["review_queue"][i]["status"] = "corrected"
                                st.session_state["review_queue"][i]["corrected_value"] = correction
                                st.rerun()
                            else:
                                st.warning("Enter a correction value before saving.")