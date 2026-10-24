
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from the same folder as this file
PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

st.set_page_config(
    page_title="LinkPilot | AI Posting Assistant",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 LinkPilot")
st.subheader("Your AI-powered social posting assistant")
st.write(
    "Describe your process, provide your draft, "
    "and let AI prepare a polished post."
)

with st.sidebar:
    st.header("Configuration")
    st.write("Project:", str(PROJECT_DIR))
    st.write("Environment file:", "Found" if ENV_FILE.is_file() else "Missing")
    st.write(
        "ASI:One API key:",
        "Detected" if os.getenv("ASI_ONE_API_KEY", "").strip() else "Missing",
    )
    st.caption("Never share your API key or commit your .env file.")

default_process = (
    "Make the post professional, concise, and engaging for LinkedIn. "
    "Start with a strong hook, keep paragraphs short, highlight the key "
    "learning or outcome, end with a question or call to action, and add "
    "3-5 relevant hashtags. Keep it under 200 words."
)

with st.form("linkpilot_form"):
    process = st.text_area(
        "What process should the AI follow?",
        value=default_process,
        height=130,
    )

    draft = st.text_area(
        "Your original post",
        placeholder="Paste your draft here...",
        height=150,
    )

    submitted = st.form_submit_button(
        "✨ Prepare post with AI",
        use_container_width=True,
    )

if submitted:
    api_key = os.getenv("ASI_ONE_API_KEY", "").strip()
    model = os.getenv("ASI_ONE_MODEL", "asi1").strip()

    if not ENV_FILE.is_file():
        st.error(
            "Cannot find .env. Create a file named .env "
            "inside the same folder as app.py."
        )
    elif not api_key:
        st.error(
            "API key is missing. Add ASI_ONE_API_KEY=your_key "
            "to your .env file, save it, and restart Streamlit."
        )
    elif not process.strip() or not draft.strip():
        st.warning("Please enter both the process and the original post.")
    else:
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.asi1.ai/v1",
                timeout=45.0,
                max_retries=1,
            )

            with st.spinner("LinkPilot is preparing your post..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are LinkPilot, an AI social media "
                                "writing assistant. Follow the user's "
                                "instructions, preserve the original meaning, "
                                "avoid inventing facts, and return only the "
                                "polished post. Do not publish anything."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Instructions:\n{process}\n\n"
                                f"Original post:\n{draft}"
                            ),
                        },
                    ],
                )

            result = response.choices[0].message.content or ""

            if result.strip():
                st.session_state["linkpilot_result"] = result.strip()
                st.success("Post generated! Review it before publishing.")
            else:
                st.error("The AI returned an empty response.")

        except Exception as exc:
            st.error(
                "The AI request failed. Check your API key, account access, "
                "model name, and API endpoint."
            )
            st.code(f"{type(exc).__name__}: {exc}")

if st.session_state.get("linkpilot_result"):
    st.divider()
    st.subheader("📝 Your prepared post")

    st.text_area(
        "Review and edit your post",
        key="linkpilot_result",
        height=220,
    )

    st.download_button(
        "⬇️ Download post",
        data=st.session_state["linkpilot_result"],
        file_name="linkpilot_post.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.info(
        "This MVP prepares and downloads posts. "
        "It does not publish directly to LinkedIn yet."
    )

st.divider()
st.caption("LinkPilot MVP • AI-assisted writing with human review")
