import difflib
import os
import re
from html import escape
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# Page setup and Gemini configuration
st.set_page_config(
    page_title="Support Chatbot",
    page_icon="🤖",
    layout="wide",
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Add GEMINI_API_KEY in Streamlit Secrets or your local .env file.")
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=api_key,
    temperature=0.5,
)


# Read FAQ blocks. Multiple Q: lines can share one A: answer.
def load_faq(path: Path):
    entries = []
    content = path.read_text(encoding="utf-8-sig").strip()

    for block in re.split(r"\n\s*\n", content):
        questions = []
        answer_lines = []

        for line in block.splitlines():
            line = line.strip()

            if line.startswith("Q:"):
                questions.append(line[2:].strip())
            elif line.startswith("A:"):
                answer_lines.append(line[2:].strip())
            elif answer_lines:
                answer_lines.append(line)

        answer = "\n".join(answer_lines).strip()
        if answer:
            entries.extend((q, answer) for q in questions if q)

    return entries


def clean_text(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


try:
    faq_data = load_faq(Path(__file__).with_name("faq.txt"))
except FileNotFoundError:
    faq_data = []

if not faq_data:
    st.warning("FAQ data is unavailable. Check faq.txt next to main.py.")


# Return the FAQ answer directly once the agent calls this tool.
@tool(return_direct=True)
def faq_lookup(query: str) -> str:
    """Look up the user's question and return the matching support FAQ answer."""
    query = clean_text(query)

    if query in {"hi", "hello", "hey", "good morning", "good evening"}:
        return "👋 Hi there! How can I help you today?"

    if not faq_data:
        return "FAQ data is not available right now."

    best_answer = "❌ Sorry, I don’t have that information."
    best_score = 0.5

    for question, answer in faq_data:
        score = difflib.SequenceMatcher(
            None, query, clean_text(question)
        ).ratio()

        if score > best_score:
            best_score = score
            best_answer = answer

    return best_answer


faq_prompt = PromptTemplate.from_template(
    """You are a customer support assistant.
Look up every question with the FAQ tool.

Available tools:
{tools}

Use the following two-line format:
Action: one of [{tool_names}]
Action Input: the user's question as plain text

Question: {input}
{agent_scratchpad}"""
)

tools = [faq_lookup]
agent = create_react_agent(llm, tools, faq_prompt, stop_sequence=False)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    max_iterations=3,
)


# Chat styling
st.markdown(
    """
    <style>
    h1 {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    h2, h3, h4 {
        color: #444 !important;
        font-weight: 600 !important;
    }
    .stCaption {
        text-align: center;
        font-size: 1rem;
        color: #666;
    }
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 16px;
        margin: 8px 0;
        max-width: 70%;
        font-size: 15px;
        line-height: 1.4;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    .chat-bubble.user {
        margin-left: auto;
        background: #e9f0ff;
        color: #222;
    }
    .chat-bubble.bot {
        margin-right: auto;
        background: #f7f7f7;
        color: #111;
    }
    .stButton>button {
        border-radius: 10px;
        background: #f0f2f6;
        border: 1px solid #ddd;
        color: #333;
        font-size: 14px;
        padding: 8px 12px;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: #e0e7ff;
        border-color: #6a11cb;
        color: #000;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize history before the sidebar buttons access it.
if "history" not in st.session_state:
    st.session_state.history = []

selected_question = None

with st.sidebar:
    st.header("⚙️ Options")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = []

    st.markdown("---")
    st.subheader("📌 Quick FAQs")

    quick_faqs = faq_data[8:13] or faq_data[:5]
    for index, (question, _) in enumerate(quick_faqs):
        if st.button(question, key=f"faq_{index}", use_container_width=True):
            selected_question = question

    st.markdown("---")
    st.subheader("📞 Contact Support")
    st.markdown("📧 support@shop.com")
    st.markdown("📞 +1-800-123-4567")


# Both the sidebar and typed questions use the same chat flow.
st.markdown("<h1>Customer Support Chatbot</h1>", unsafe_allow_html=True)
st.caption("Ask me about orders, returns, or anything else!")

user_input = st.chat_input("Type your message...")
question = selected_question or user_input

if question:
    st.session_state.history.append({"role": "user", "text": question})

    with st.spinner("Checking the FAQs…"):
        try:
            response = agent_executor.invoke({"input": question})
            answer = response["output"]
        except Exception as exc:
            error = str(exc).lower()
            if "429" in error or "resource_exhausted" in error:
                answer = "The Gemini request limit was reached. Please try again later."
            else:
                answer = "The support assistant could not complete this request. Please try again."

    st.session_state.history.append({"role": "assistant", "text": answer})

for message in st.session_state.history:
    role = "user" if message["role"] == "user" else "bot"
    safe_text = escape(message["text"])
    st.markdown(
        f"<div class='chat-bubble {role}'>{safe_text}</div>",
        unsafe_allow_html=True,
    )
