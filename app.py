import streamlit as st

from interviewer import final_report, next_question
from resume import extract_text
from sarvam_client import SARVAM_API_KEY, SarvamError, stt, tts

st.set_page_config(page_title="Mock Interviewer", page_icon="🎙️")
st.title("🎙️ Mock Interviewer")
st.caption("Upload your resume. Get interviewed by voice. Get a feedback report.")

import sarvam_client

if not SARVAM_API_KEY:
    key = st.text_input("Paste your Sarvam API key to start", type="password")
    if not key.strip():
        st.stop()
    sarvam_client.HEADERS["api-subscription-key"] = key.strip()

ss = st.session_state
for k, v in {"started": False, "done": False, "history": [], "question": "",
             "q_audio": None, "played": False, "resume": "", "report": "", "err": ""}.items():
    ss.setdefault(k, v)

# ---------- Sidebar: setup ----------
with st.sidebar:
    st.header("Setup")
    pdf = st.file_uploader("Resume (PDF)", type=["pdf"])
    role = st.text_input("Target role", "Software Engineer Intern")
    n_q = st.slider("Number of questions", 3, 10, 5)
    voice_lang = st.selectbox("Interviewer voice", ["en-IN", "hi-IN"])
    start = st.button("Start interview", type="primary", disabled=pdf is None)
    if st.button("Reset"):
        for k in ["started", "done", "history", "question", "q_audio", "played", "resume", "report", "err"]:
            del ss[k]
        st.rerun()

def ask_next():
    ss.question = next_question(ss.resume, role, ss.history)
    ss.q_audio = tts(ss.question, voice_lang)
    ss.played = False

# ---------- Start ----------
if start and pdf:
    try:
        with st.spinner("Reading your resume..."):
            ss.resume = extract_text(pdf.getvalue())
        if not ss.resume:
            st.error("No text found in this PDF (it may be a scan). Try a text-based PDF.")
            st.stop()
        ss.history, ss.done, ss.report = [], False, ""
        with st.spinner("Preparing the first question..."):
            ask_next()
        ss.started = True
    except SarvamError as e:
        st.error(str(e)); st.stop()

# ---------- Interview ----------
if ss.started and not ss.done:
    i = len(ss.history)
    st.progress(i / n_q, text=f"Question {i + 1} of {n_q}")
    st.subheader(ss.question)
    if ss.q_audio:
        st.audio(ss.q_audio, format="audio/wav", autoplay=not ss.played)
        ss.played = True

    answer, key = None, i
    mic = st.audio_input("Record your answer", key=f"mic_{key}")
    typed = st.text_area("...or type your answer", key=f"txt_{key}")
    submit = st.button("Submit typed answer", key=f"sub_{key}")

    try:
        if mic:
            with st.spinner("Transcribing..."):
                answer, _ = stt(mic.getvalue())
            if not answer.strip():
                st.warning("Could not hear anything. Please record again.")
                answer = None
        elif submit and typed.strip():
            answer = typed.strip()

        if answer:
            ss.history.append({"q": ss.question, "a": answer})
            if len(ss.history) >= n_q:
                with st.spinner("Writing your feedback report..."):
                    ss.report = final_report(ss.resume, role, ss.history)
                ss.done = True
            else:
                with st.spinner("Next question..."):
                    ask_next()
            st.rerun()
    except SarvamError as e:
        st.error(str(e))

# ---------- Report ----------
if ss.done:
    st.success("Interview complete!")
    st.markdown(ss.report)
    with st.expander("Full transcript"):
        for n, h in enumerate(ss.history, 1):
            st.markdown(f"**Q{n}. {h['q']}**\n\n{h['a']}")
    st.download_button("Download report", ss.report, file_name="interview_report.md")
