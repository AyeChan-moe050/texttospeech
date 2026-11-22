import gc
import io
import tempfile
from datetime import datetime
from pathlib import Path
import streamlit as st

from export_doc import save_docx, save_markdown
from transcribe import transcribe_audio

st.set_page_config(
    page_title="Myanmar Audio to Full Text",
    page_icon="📝",
    layout="wide",
)
st.title("📝 Myanmar Audio to Full Text")
st.caption(
    "အသံဖိုင်ထဲမှာ ပြောထားတဲ့ စကားအကုန်လုံးကို စာသား (Full Text) အဖြစ် ပြန်ထုတ်ပေးပြီး .md / .docx ဖိုင်ဖြင့် သိမ်းဆည်းနိုင်ပါသည်။"
)

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
        index=1,
        help="Streamlit Cloud မှာ memory မပြည့်စေရန် 'tiny' သို့မဟုတ် 'base' ကို ရွေးပါ။",
    )

uploaded_file = st.file_uploader(
    "Upload meeting audio or video",
    type=["mp3", "wav", "m4a", "mp4", "ogg", "webm"],
)


def _build_export_buffers(full_text: str) -> tuple[bytes, bytes, str, str]:
    """Build in-memory .md and .docx bytes for the full transcribed text."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_filename = f"full_transcript_{stamp}.md"
    docx_filename = f"full_transcript_{stamp}.docx"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        md_file = save_markdown(full_text, tmp_path / md_filename)
        docx_file = save_docx(
            full_text,
            tmp_path / docx_filename,
            title="အသံဖိုင် စာသားမှတ်တမ်း (Full Transcript)",
        )
        md_bytes = md_file.read_bytes()
        docx_bytes = docx_file.read_bytes()

    return md_bytes, docx_bytes, md_filename, docx_filename


if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Convert Audio to Full Text", type="primary"):
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_audio_path = tmp.name

        try:
            with st.status("Processing recording...", expanded=True) as status:
                st.write("Transcribing full audio with Whisper...")
                full_text = transcribe_audio(
                    temp_audio_path,
                    model_size=whisper_model,
                    language=language_code,
                )
                status.update(label="Full text ready!", state="complete")

            md_bytes, docx_bytes, md_name, docx_name = _build_export_buffers(full_text)
            st.session_state["full_text"] = full_text
            st.session_state["md_bytes"] = md_bytes
            st.session_state["docx_bytes"] = docx_bytes
            st.session_state["md_name"] = md_name
            st.session_state["docx_name"] = docx_name
            gc.collect()
        except Exception as exc:
            st.error(f"Error while transcribing audio: {exc}")
        finally:
            Path(temp_audio_path).unlink(missing_ok=True)

if "full_text" in st.session_state:
    edited_text = st.text_area(
        "အသံဖိုင်ထဲမှ ပြောစကား အပြည့်အစုံ (လိုအပ်ပါက ပြင်ဆင်နိုင်ပါသည်):",
        value=st.session_state["full_text"],
        height=420,
    )

    if edited_text != st.session_state["full_text"]:
        st.session_state["full_text"] = edited_text
        md_bytes, docx_bytes, md_name, docx_name = _build_export_buffers(edited_text)
        st.session_state["md_bytes"] = md_bytes
        st.session_state["docx_bytes"] = docx_bytes
        st.session_state["md_name"] = md_name
        st.session_state["docx_name"] = docx_name

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Markdown (.md)",
            data=io.BytesIO(st.session_state["md_bytes"]),
            file_name=st.session_state["md_name"],
            mime="text/markdown",
        )
    with col2:
        st.download_button(
            label="Download Word (.docx)",
            data=io.BytesIO(st.session_state["docx_bytes"]),
            file_name=st.session_state["docx_name"],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
