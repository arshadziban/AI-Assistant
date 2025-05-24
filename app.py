import streamlit as st
import requests

# Configurations
OLLAMA_API_URL = "your_ollama_api_url_here"  # Replace with your Ollama API URL
MODEL_NAME = "llama3.2"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Page configuration
st.set_page_config(page_title="AI Assistant", page_icon="💬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }

    .chat-container {
        max-width: 850px;
        
        margin: 0 auto;
        padding-bottom: 20px;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .chat-message {
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        max-width: 75%;
        font-family: "Segoe UI", sans-serif;
        font-size: 16px;
        line-height: 1.6;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.07);
        word-wrap: break-word;
    }

    .user-msg {
        background-color: #1a73e8;
        color: #fff;
        margin-left: auto;
        text-align: left;
    }

    .ai-msg {
        background-color: #f4f4f9;
        color: #111;
        margin-right: auto;
        border: 1px solid #e0e0e0;
    }

    .title-container {
        text-align: center;
        margin-bottom: 2rem;
    }

    .stTextInput > div > div > input {
        border-radius: 4px;
        border: 1px solid #ccc;
        padding: 10px 16px;
        font-size: 16px;
    }

    .stButton > button {
        border-radius: 4px;
        background-color: #1a73e8;
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 15px;
    }

    .stButton > button:hover {
        background-color: #155ab6;
    }

    .sidebar .stSelectbox {
        margin-bottom: 1rem;
    }

    .input-area {
        position: sticky;
        bottom: 0;
        background-color: #0e1117;
        padding: 1rem 0;
        border-top: 1px solid #333;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Settings")
    model_name = st.selectbox(
        "Select Model",
        ["llama3.2", "llama3", "codellama", "mistral"],
        index=0
    )

    if st.button("Test Connection", use_container_width=True):
        try:
            test_response = requests.get("your_ollama_api_url_here/models") 
            if test_response.status_code == 200:
                st.success("Connected successfully.")
                models = test_response.json().get('models', [])
                if models:
                    st.markdown("**Available models:**")
                    for model in models:
                        st.write(f"- {model['name']}")
            else:
                st.error("Connection failed.")
        except Exception as e:
            st.error(f"Error: {str(e)[:50]}...")

    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.input_key += 1
        st.rerun()

# Header
st.markdown('<div class="title-container">', unsafe_allow_html=True)
st.title("AI Assistant")
st.markdown('</div>', unsafe_allow_html=True)

# Chat messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg['sender'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-msg">
                <strong>User</strong><br>
                {msg['text']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-msg">
                <strong>Assistant</strong><br>
                {msg['text']}
            </div>
            """, unsafe_allow_html=True)

# Welcome message
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666;">
        <h4>Welcome to the AI Assistant</h4>
    </div>
    """, unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-area">', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        key=f"user_input_{st.session_state.input_key}",
        label_visibility="collapsed"
    )
with col2:
    send_button = st.button("Send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Message handling
if send_button and user_input.strip():
    message_text = user_input.strip()
    st.session_state.messages.append({'sender': 'user', 'text': message_text})
    st.session_state.input_key += 1

    with st.spinner("Processing response..."):
        payload = {
            "model": model_name,
            "prompt": message_text,
            "stream": False,
            "options": {"temperature": 0.7}
        }

        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            ai_reply = data.get('response', 'No response received.')
        except requests.exceptions.ConnectionError:
            ai_reply = "Connection error. Please ensure Ollama is running."
        except requests.exceptions.Timeout:
            ai_reply = "Request timed out. Please try again."
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                ai_reply = f"Model '{model_name}' not found. Please ensure it is available."
            else:
                ai_reply = f"HTTP Error {e.response.status_code}"
        except Exception as e:
            ai_reply = f"Error: {str(e)}"

    st.session_state.messages.append({'sender': 'ai', 'text': ai_reply})
    st.rerun()
