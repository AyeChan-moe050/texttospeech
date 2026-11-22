import tempfile
from datetime import datetime
from pathlib import Path
import streamlit as st

from export_doc import save_docx, save_markdown
from summarize import generate_minutes
from transcribe import transcribe_audio

st.set_page_config(
    page_title="Myanmar Meeting Minutes Generator",
    page_icon="📝",
    layout="wide",
)
st.title("📝 Speech-to-Text Meeting Minutes Generator")
st.caption(
    "Upload a Myanmar meeting recording, transcribe it with Whisper, and export structured minutes."
)

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    language_code = st.selectbox(
        "Audio Language",
        options=["my", "en"],
        index=0,
    )
    whisper_model = st.selectbox(
        "Whisper Model",
        options=["tiny", "base", "small", "medium", "large"],
        index=2,
    )
    llm_model = st.text_input("Ollama Model", value="llama3.2")
    ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")

uploaded_file = st.file_uploader(
    "Upload meeting audio or video",
    type=["mp3", "wav", "m4a", "mp4", "ogg", "webm"],
)

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Generate Meeting Minutes", type="primary"):
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_audio_path = tmp.name

        try:
            with st.status("Processing recording...", expanded=True) as status:
                st.write("1/2 Transcribing audio with Whisper...")
                transcript = transcribe_audio(
                    temp_audio_path,
                    model_size=whisper_model,
                    language=language_code,
                )

                st.write("2/2 Structuring meeting minutes...")
                minutes = generate_minutes(
                    transcript,
                    model=llm_model,
                    ollama_url=ollama_url,
                )
                status.update(label="Meeting minutes ready!", state="complete")

            st.session_state["transcript"] = transcript
            st.session_state["minutes"] = minutes
        finally:
            Path(temp_audio_path).unlink(missing_ok=True)

if "minutes" in st.session_state:
    tab1, tab2 = st.tabs(["Edit & Export Minutes", "Raw Transcript"])

    with tab1:
        edited_minutes = st.text_area(
            "Review or edit generated minutes before downloading:",
            value=st.session_state["minutes"],
            height=380,
        )

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("outputs")
        md_path = save_markdown(edited_minutes, out_dir / f"meeting_minutes_{stamp}.md")
        docx_path = save_docx(edited_minutes, out_dir / f"meeting_minutes_{stamp}.docx")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Markdown (.md)",
                data=md_path.read_bytes(),
                file_name=md_path.name,
                mime="text/markdown",
            )
        with col2:
            st.download_button(
                label="Download Word (.docx)",
                data=docx_path.read_bytes(),
                file_name=docx_path.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

    with tab2:
        st.text_area(
            "Transcript",
            value=st.session_state["transcript"],
            height=380,
            disabled=True,
        )
