import streamlit as st
import os
from dotenv import load_dotenv

from utils.extractor import extract_text_from_file, check_tessdata
from utils.storage import upload_to_blob, list_blobs, download_blob
from utils.ai import answer_questions, summarize_document

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Question Paper AI",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Question Paper AI")
st.caption("Upload a question paper or paste text — get answers, summaries, and chat with your document.")

# ── Session state ─────────────────────────────────────────────────────────────
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_summary" not in st.session_state:
    st.session_state.doc_summary = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📥 Load Document")

    input_mode = st.radio("Input method", ["Upload file", "Paste text", "Load from Azure"])

    # ── Mode 1: File upload ──
    if input_mode == "Upload file":
        uploaded = st.file_uploader(
            "Upload PDF, image, or text file",
            type=["pdf", "png", "jpg", "jpeg", "txt", "docx"],
        )
        if uploaded and st.button("Extract & Load", type="primary"):
            with st.spinner("Extracting text from document..."):
                is_ok, warning_msg = check_tessdata(st.session_state.selected_language)
                if not is_ok:
                    st.error(warning_msg)
                else:
                    file_bytes = uploaded.read()
                    text = extract_text_from_file(
                        file_bytes,
                        uploaded.name,
                        language=st.session_state.selected_language,
                    )

                    if text.strip():
                        st.session_state.document_text = text
                        st.session_state.doc_name = uploaded.name
                        st.session_state.chat_history = []
                        st.session_state.doc_summary = ""

                        blob_url = upload_to_blob(file_bytes, uploaded.name)
                        if blob_url:
                            st.success("✅ Uploaded to Azure Storage")
                        else:
                            st.info("ℹ️ Azure Storage not configured — file loaded locally only")

                        st.success(f"✅ Text extracted ({len(text):,} characters)")
                    else:
                        st.error("Could not extract text. Check your Azure Document Intelligence keys.")

    # ── Mode 2: Paste text ──
    elif input_mode == "Paste text":
        pasted = st.text_area("Paste your question paper or notes here", height=250)
        doc_name = st.text_input("Document name (optional)", value="pasted_document.txt")
        if st.button("Load Text", type="primary"):
            if pasted.strip():
                st.session_state.document_text = pasted.strip()
                st.session_state.doc_name = doc_name
                st.session_state.chat_history = []
                st.session_state.doc_summary = ""
                st.success(f"✅ Text loaded ({len(pasted):,} characters)")
            else:
                st.warning("Please paste some text first.")

    # ── Mode 3: Load from Azure ──
    elif input_mode == "Load from Azure":
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        if not conn_str:
            st.warning("Azure Storage not configured in .env")
        else:
            blobs = list_blobs()
            if blobs:
                selected = st.selectbox("Choose a file from Azure Storage", blobs)
                if st.button("Load from Azure", type="primary"):
                    with st.spinner("Downloading from Azure..."):
                        file_bytes = download_blob(selected)
                        text = extract_text_from_file(
                            file_bytes,
                            selected,
                            language=st.session_state.selected_language,
                        )
                        st.session_state.document_text = text
                        st.session_state.doc_name = selected
                        st.session_state.chat_history = []
                        st.session_state.doc_summary = ""
                        st.success("✅ Loaded from Azure Storage")
            else:
                st.info("No files found in Azure Storage yet.")

    st.divider()

    # ── Language selector ──
    st.subheader("🌐 Response Language")
    selected_language = st.selectbox(
        "Answer questions in:",
        options=[
            "English", "Hindi", "Gujarati", "Marathi", "Tamil",
            "Telugu", "Bengali", "French", "Spanish", "German", "Arabic"
        ],
        index=["English", "Hindi", "Gujarati", "Marathi", "Tamil",
               "Telugu", "Bengali", "French", "Spanish", "German", "Arabic"
               ].index(st.session_state.selected_language),
    )
    st.session_state.selected_language = selected_language

    st.divider()

    # ── Document status ──
    if st.session_state.document_text:
        st.success(f"**Active:** {st.session_state.doc_name}")
        st.caption(f"{len(st.session_state.document_text):,} characters loaded")

        if st.button("🗑️ Clear document"):
            st.session_state.document_text = ""
            st.session_state.chat_history = []
            st.session_state.doc_summary = ""
            st.session_state.doc_name = ""
            st.rerun()
    else:
        st.info("No document loaded yet.")

    st.divider()
    st.caption("Powered by Groq (Llama 3.3) · Azure Blob Storage · Azure Doc Intelligence")

# ── Main area ─────────────────────────────────────────────────────────────────
if not st.session_state.document_text:
    st.info("👈 Load a document from the sidebar to get started.")
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Chat with Document", "✅ Answer All Questions", "📋 Document Summary"])

# ── Tab 1: Chat ───────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Chat with your document")
    st.caption("Ask anything — 'What is this about?', 'Explain question 3', 'List all topics covered'")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about the document...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = answer_questions(
                        st.session_state.document_text,
                        user_input,
                        st.session_state.chat_history,
                        language=st.session_state.selected_language,
                    )
                    st.markdown(response)

                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

# ── Tab 2: Answer all questions ───────────────────────────────────────────────
with tab2:
    st.subheader("Answer all questions in the document")
    st.caption("The AI will find every question in the paper and answer them all at once.")

    col1, col2 = st.columns([2, 1])
    with col1:
        custom_instruction = st.text_input(
            "Custom instruction (optional)",
            placeholder="e.g. Answer in detail, or Answer briefly, or Focus on maths questions",
        )
    with col2:
        answer_btn = st.button("🚀 Answer All Questions", type="primary", use_container_width=True)

    if answer_btn:
        prompt = "Please find and answer ALL questions in this document."
        if custom_instruction:
            prompt += f" Instruction: {custom_instruction}"

        with st.spinner("Answering all questions... this may take a moment"):
            try:
                result = answer_questions(
                    st.session_state.document_text,
                    prompt,
                    [],
                    language=st.session_state.selected_language,
                )
                st.markdown(result)

                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": result})

            except Exception as e:
                st.error(f"Error: {e}")

# ── Tab 3: Summary ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Document Summary")

    if st.session_state.doc_summary:
        st.markdown(st.session_state.doc_summary)
    else:
        if st.button("📋 Generate Summary", type="primary"):
            with st.spinner("Summarizing document..."):
                try:
                    summary = summarize_document(
                        st.session_state.document_text,
                        language=st.session_state.selected_language,
                    )
                    st.session_state.doc_summary = summary
                    st.markdown(summary)
                except Exception as e:
                    st.error(f"Error: {e}")

    with st.expander("📄 View raw extracted text"):
        st.text_area("Extracted text", st.session_state.document_text, height=400)