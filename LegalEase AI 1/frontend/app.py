import re
import sys
from pathlib import Path

# Make project root importable when launched via `streamlit run`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import streamlit as st

from ai_core.generator import (format_docx, format_html_preview, format_pdf,
                               sanitize_text)
from config import API_URL, LOGO_PATH, ensure_logo

ensure_logo()
st.set_page_config(page_title="LegalEase", layout="centered")

# ---- Header
_, mid, _ = st.columns([1, 2, 1])
with mid:
    st.image(str(LOGO_PATH), use_container_width=True)
st.markdown("<h2 style='text-align:center;'>AI Legal Document Generator</h2>",
            unsafe_allow_html=True)

# ---- State
for key, default in {"current_text": "", "doc_type": "", "terms": "",
                     "show_edit": False}.items():
    st.session_state.setdefault(key, default)

# ---- Inputs
document_type = st.text_input("Document Type (Ex: Agreement, Contract, NDA)")
parties = st.text_area("Parties Involved")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)")
dates = st.text_input("Effective Date")

# ---- Generate
if st.button("Generate Document"):
    if not document_type.strip() or not parties.strip():
        st.warning("Please fill in at least Document Type and Parties Involved.")
    else:
        with st.spinner("Generating your document..."):
            try:
                resp = requests.post(
                    f"{API_URL}/generate",
                    json={"document_type": document_type, "parties": parties,
                          "terms": terms, "dates": dates},
                    timeout=180,
                )
                if resp.status_code == 200:
                    st.session_state.current_text = sanitize_text(
                        resp.json()["document"])
                    st.session_state.doc_type = document_type
                    st.session_state.terms = terms
                    st.session_state.show_edit = False
                    st.session_state.pop("editor", None)
                    st.success("Document Generated Successfully!")
                else:
                    detail = resp.json().get("detail", resp.text)
                    st.error(f"Error {resp.status_code}: {detail}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Start the app with "
                         "`python run.py`.")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

# ---- Preview, edit, download
if st.session_state.current_text:
    if st.button("✏️ Click to Edit Document"):
        st.session_state.show_edit = not st.session_state.show_edit

    if st.session_state.show_edit:
        st.session_state.current_text = st.text_area(
            "Edit Document Below:",
            value=st.session_state.current_text,
            height=300, key="editor")

    styled = format_html_preview(st.session_state.current_text)
    st.markdown(
        "<div style='background:#0f172a;color:#e2e8f0;padding:20px;"
        "border-radius:10px;max-height:420px;overflow-y:auto;"
        f"font-family:Georgia,serif;'>{styled}</div>",
        unsafe_allow_html=True,
    )

    text = st.session_state.current_text
    doc_type = st.session_state.doc_type
    saved_terms = st.session_state.terms
    base = re.sub(r"[^a-z0-9]+", "_", doc_type.lower()).strip("_") or "document"

    st.download_button("📄 Download as .TXT", data=text,
                       file_name=f"{base}.txt", mime="text/plain")
    st.download_button(
        "📝 Download as .DOCX", data=format_docx(text, doc_type, saved_terms),
        file_name=f"{base}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    st.download_button("📕 Download as .PDF",
                       data=format_pdf(text, doc_type, saved_terms),
                       file_name=f"{base}.pdf", mime="application/pdf")
else:
    st.info("Click 'Generate Document' to start")