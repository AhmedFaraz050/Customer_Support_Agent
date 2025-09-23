
# Customer Support Chatbot

A sleek and modern customer support chatbot built with **Streamlit**, **LangChain**, and **Google Gemini**. This chatbot can answer FAQs, respond to greetings, and provide helpful responses using a ReAct agent and a fuzzy search over your FAQ data.

---

## Features

- Answer frequently asked questions from `faq.txt`.
- Respond to greetings like "hi", "hello", "hey", etc.
- Uses fuzzy matching to find the best FAQ answer.
- Custom ReAct agent powered by **Google Gemini**.
- Sleek modern styling with chat bubbles for user and bot.
- Sidebar with quick FAQ buttons and contact information.
- Supports multiple questions per FAQ entry.

---

## Project Structure

```

├── main.py          # Main Streamlit application
├── faq.txt          # FAQ data file
├── .env             # Environment variables (API key for Gemini)
├── .gitignore       # Git ignore file
├── requirements.txt # Python dependencies
└── README.md        # Project documentation

````

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/support-chatbot.git
cd support-chatbot
````

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Add your Gemini API key**

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_google_gemini_api_key
```

**Important:** Do **not** commit `.env` to GitHub.

5. **Run the Streamlit app**

```bash
streamlit run main.py
```

---

## Usage

* Type your question in the chat input.
* Click on quick FAQ buttons in the sidebar to test common questions.
* The bot will respond using the Gemini-powered LangChain agent.
* Greetings like "hi", "hello", "hey" will also receive a friendly response.

---

## FAQ Example

Example entries in `faq.txt`:

```
Q: How do I return a product?
Q: I want to send back my order.
A: You can return a product within 30 days using our online return form. Make sure the product is in its original condition.

Q: What are the shipping charges?
A: Standard shipping is free for orders over $50. For orders under $50, shipping costs $5.
```

---

## Dependencies

* streamlit
* python-dotenv
* langchain
* langchain-google-genai
* difflib (built-in)
* re (built-in)

---

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m "Add new feature"`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a Pull Request.

---
