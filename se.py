import streamlit as st
import requests
import google.generativeai as genai
import re, difflib

# --- Configure Gemini ---
API_KEY = "AIzaSyDDwpm0Qt8-L424wY1oXcJThjZwFDeiUNI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Gemini Response ---
def get_gemini_response(query: str) -> str:
    try:
        resp = model.generate_content(query)
        return resp.text
    except Exception as e:
        return f"Error from Gemini: {e}"

# --- DuckDuckGo Search ---
def get_duckduckgo_links(query: str, max_results: int = 10):
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1}
    res = requests.get(url, params=params).json()
    links = []
    if "RelatedTopics" in res:
        for topic in res["RelatedTopics"]:
            if "FirstURL" in topic:
                links.append(topic["FirstURL"])
            if "Topics" in topic:
                for sub in topic["Topics"]:
                    if "FirstURL" in sub:
                        links.append(sub["FirstURL"])
    return links[:max_results]

# --- Normalization + Fuzzy Matching ---
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # keep only letters/spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_predefined_response(prompt: str, predefined: dict) -> str | None:
    norm = normalize(prompt)
    keys = list(predefined.keys())
    match = difflib.get_close_matches(norm, keys, n=1, cutoff=0.6)
    if match:
        return predefined[match[0]]
    return None

# --- Predefined Responses (add your 100+ entries here) ---
predefined_info = {
    "who are you":"I am Max your Intelligent Assistant"
    "what is your name": "I am Max, an AI built by Debayan Das.",
    "who made you": "I was created by Debayan Das.",
    "what can you do": "I can search the web, answer with Gemini, and chat with you.",
    "who is debayan": "Debayan Das is my creator, a young developer from India.",
    "are you a search engine": "I combine AI with DuckDuckGo search results.",
    "do you know programming": "Yes, I can explain and generate code in Python, JavaScript, and more.",
    "what is gemini": "Gemini is Google's advanced AI model that powers my responses.",
    "what is duckduckgo": "DuckDuckGo is a privacy-friendly search engine that I use to fetch links.",
    "do you learn": "I don’t learn from chats directly, but I have knowledge up to 2025.",
    "are you free": "Yes, you can use me freely here.",
    "are you better than chatgpt": "I am designed differently, but I try to be as helpful as possible.",
    "can you write code": "Yes, I can generate, explain, and debug code.",
    "can you solve math": "Yes, I can solve equations, derivatives, integrals, and word problems.",
    "who owns you": "I belong to Debayan Das, my developer.",
    "how old are you": "I was created in 2025, so I am very new.",
    "where do you live": "I live in the cloud, inside this app.",
    "what is your purpose": "My purpose is to assist, search, and answer questions interactively.",
    "are you maxai": "Yes, my name is Max, also called MaxAI sometimes.",

}

# --- Streamlit Page ---
st.set_page_config(page_title="Max", page_icon="🔍")
st.title("🎓 Max")


if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="https://wallpapercave.com/wp/wp9110432.jpg"):
            st.markdown(msg["content"])
    elif msg["role"] == "ai":
        with st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg"):
            st.markdown(msg["content"])
    elif msg["role"] == "links":
        with st.chat_message("assistant", avatar="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg"):
            for link in msg["content"]:
                st.markdown(f"- [{link}]({link})")


if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    

    response = get_predefined_response(prompt, predefined_info)
    if response:
        ai_text = response
    else:
        # Gemini AI response
        with st.spinner("Gemini is thinking..."):
            ai_text = get_gemini_response(prompt)
    
    st.session_state.messages.append({"role": "ai", "content": ai_text})
    

    if not response:
        with st.spinner("Searching..."):
            links = get_duckduckgo_links(prompt, max_results=15)
        st.session_state.messages.append({"role": "links", "content": links})
    
    st.rerun()
