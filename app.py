import streamlit as st
from app.services import extract_pdf, chunk_by_sections, build_review_queue
from app.services import extract_payment, extract_termination, extract_renewal
import datetime
import asyncio

st.set_page_config(page_title="ContractIQ", layout="wide")
st.title("ContractIQ")
st.caption("Automated first-pass contract review")


uploaded_file = st.file_uploader("Upload a contract PDF", type=["pdf"])

if uploaded_file:
    if st.button("Extract"):
        with st.spinner("Reading and extracting contract..."):
            file_bytes = uploaded_file.read()
            
            # run your existing pipeline
            result = extract_pdf(file_bytes)
            chunks = chunk_by_sections(result["text"])
            
            fields = {
                "payment_terms": asyncio.run(extract_payment(chunks)),
                "termination": asyncio.run(extract_termination(chunks)),
                "auto_renewal": asyncio.run(extract_renewal(chunks))
            }
            
            review_queue = build_review_queue(fields)
            
            # store in session state
            st.session_state["fields"] = fields
            st.session_state["review_queue"] = review_queue
            st.session_state["filename"] = uploaded_file.name

# --- RESULTS SCREEN ---
if "fields" in st.session_state:
    fields = st.session_state["fields"]
    review_queue = st.session_state["review_queue"]

    st.divider()
    st.subheader(f"Results — {st.session_state['filename']}")

    # --- EXTRACTED FIELDS ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Payment Terms")
        pt = fields["payment_terms"]
        st.write("**Amount:**", pt.payment_terms)
        st.write("**Notes:**", pt.notes)
        st.write("**Source:**", pt.raw_text)
        confidence = pt.confidence
        color = "green" if confidence == "high" else "orange" if confidence == "medium" else "red"
        st.markdown(f"**Confidence:** :{color}[{confidence}]")

    with col2:
        st.markdown("### Termination")
        t = fields["termination"]
        st.write("**Notice Period:**", t.notice_period)
        st.write("**Type:**", t.termination_type)
        st.write("**Condition:**", t.condition)
        st.write("**Source:**", t.raw_text)
        confidence = t.confidence
        color = "green" if confidence == "high" else "orange" if confidence == "medium" else "red"
        st.markdown(f"**Confidence:** :{color}[{confidence}]")

    with col3:
        st.markdown("### Auto-Renewal")
        ar = fields["auto_renewal"]
        st.write("**Auto-Renewal:**", ar.is_auto_renewal)
        st.write("**Notice Required:**", ar.notice_required)
        st.write("**Terms:**", ar.renewal_terms)
        st.write("**Source:**", ar.raw_text)
        confidence = ar.confidence
        color = "green" if confidence == "high" else "orange" if confidence == "medium" else "red"
        st.markdown(f"**Confidence:** :{color}[{confidence}]")

    # --- REVIEW QUEUE ---
    st.divider()
    st.subheader("Review Queue")

    if not review_queue:
        st.success("No items flagged for review.")
    else:
        for i, item in enumerate(review_queue):
            with st.expander(f"⚠️ {item['field_name']} — {item['reason']}"):
                st.write("**Extracted Value:**", item.raw_text)
                st.write("**Confidence:**", item.confidence)
                st.write("**Status:**", st.session_state["review_queue"][i]["status"])

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Confirm", key=f"confirm_{i}"):
                        st.session_state["review_queue"][i]["status"] = "confirmed"
                        st.rerun()
                with col_b:
                    correction = st.text_input("Correction", key=f"correct_{i}")
                    if st.button("Save Correction", key=f"save_{i}"):
                        st.session_state["review_queue"][i]["status"] = "corrected"
                        st.session_state["review_queue"][i]["corrected_value"] = correction
                        st.rerun()