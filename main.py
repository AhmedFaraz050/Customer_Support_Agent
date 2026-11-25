import os
import re
import difflib
from dotenv import load_dotenv
import streamlit as st

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool, create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

# ------------------------
# Load environment + LLM
# ------------------------
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.5)

# ------------------------
# Load FAQ data (multi-Q fix)
# ------------------------
faq_data = []
try:
    with open("faq.txt", "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        questions, answer = [], ""
        for line in lines:
            if line.startswith("Q:"):
                questions.append(line.replace("Q:", "").strip())
            elif line.startswith("A:"):
                answer = line.replace("A:", "").strip()
        for q in questions:
            faq_data.append({"question": q, "answer": answer})

except FileNotFoundError:
    faq_data.append(
        {"question": "fallback", "answer": "FAQ data is not available right now."}
    )

# ------------------------
# Helpers
# ------------------------
def clean_text(text: str) -> str:
    """Lowercase + remove punctuation for better fuzzy match."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

# ------------------------
# FAQ Lookup Tool with Greetings
# ------------------------
@tool
def faq_lookup(query: str) -> str:
    """Retrieve the best matching FAQ answer using fuzzy similarity search."""
    query_clean = clean_text(query)

    # Greetings
    if query_clean in ["hi", "hello", "hey", "good morning", "good evening"]:
        return "👋 Hi there! How can I help you today?"

    best_match, best_score = None, 0.0

    for item in faq_data:
        score = difflib.SequenceMatcher(
            None, query_clean, clean_text(item["question"])
        ).ratio()
        if score > best_score:
            best_score, best_match = score, item

    if best_match and best_score > 0.5:  # relaxed threshold
        return best_match["answer"]
    else:
        return "❌ Sorry, I don’t have that information."

# ------------------------
# Custom ReAct Prompt
# ------------------------
faq_prompt = PromptTemplate.from_template("""
You are a helpful customer support assistant.

Tools:
{tools}

You can use these tool names: {tool_names}

Use this format only:

Question: the input question you must answer
Thought: reasoning
Action: one of [{tool_names}]
Action Input: text
Observation: tool output
Final Answer: user-facing response

If the tool returns "❌ Sorry, I don’t have that information.", 
then reply with exactly that.

Begin!

Question: {input}
{agent_scratchpad}
""")

# ------------------------
# Create Agent
# ------------------------
tools = [faq_lookup]
agent = create_react_agent(llm, tools, faq_prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=False, handle_parsing_errors=True
)

# ------------------------
# Streamlit Page Config
# ------------------------
st.set_page_config(page_title="Support Chatbot", page_icon="🤖", layout="wide")

# ------------------------
# Modern CSS Styling (your styling kept)
# ------------------------
st.markdown("""
<style>
/* Headings */
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

/* Caption */
.stCaption {
    text-align: center;
    font-size: 1rem;
    color: #666 !important;
}

/* Chat bubbles */
.chat-bubble {
    padding: 12px 18px;
    border-radius: 16px;
    margin: 8px 0;
    max-width: 70%;
    font-size: 15px;
    line-height: 1.4;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
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

/* Sidebar FAQ Buttons */
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
""", unsafe_allow_html=True)

# ------------------------
# Sidebar
# ------------------------
with st.sidebar:
    st.header("⚙️ Options")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = []
    st.markdown("---")
    st.subheader("📌 Quick FAQs")
    for item in faq_data[8:13]:
        if st.button(item["question"], use_container_width=True):
            st.session_state.history.append({"role": "user", "text": item["question"]})
            response = agent_executor.invoke({"input": item["question"]})
            answer = response.get("output") or response.get("output_text")
            st.session_state.history.append({"role": "assistant", "text": answer})
    st.markdown("---")
    st.subheader("📞 Contact Support")
    st.markdown("📧 support@shop.com")
    st.markdown("📞 +1-800-123-4567")

# ------------------------
# Session State
# ------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------
# Main Chat Title
# ------------------------
st.markdown("<h1> Customer Support Chatbot</h1>", unsafe_allow_html=True)
st.caption("Ask me about orders, returns, or anything else!")

# ------------------------
# Chat Display
# ------------------------
for msg in st.session_state.history:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(f"<div class='chat-bubble {role_class}'>{msg['text']}</div>", unsafe_allow_html=True)

# ------------------------
# Chat Input
# ------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append({"role": "user", "text": user_input})

    response = agent_executor.invoke({"input": user_input})
    answer = response.get("output") or response.get("output_text")

    st.session_state.history.append({"role": "assistant", "text": answer})
    st.markdown(f"<div class='chat-bubble bot'>{answer}</div>", unsafe_allow_html=True)
