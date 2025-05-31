import streamlit as st
import requests
import json
from datetime import datetime
import re

# Configure page
st.set_page_config(
    page_title="Empaai",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Subtle, calming CSS
st.markdown("""
<style>
    .main > div {
        padding: 1rem 2rem;
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1.5rem;
    }
    
    .main-title {
        font-size: 1.8rem;
        color: #4a5568;
        font-weight: 300;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 300;
    }
    
    .chat-container {
        max-height: 60vh;
        overflow-y: auto;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .user-message {
        background-color: #f7fafc;
        color: #2d3748;
        margin-left: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .ai-message {
        background-color: #fefefe;
        color: #4a5568;
        margin-right: 2rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .input-container {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #f1f5f9;
    }
    
    .stTextArea textarea {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        padding: 0.75rem !important;
        background-color: #fefefe !important;
        color: #4a5568 !important;
        resize: none !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #cbd5e0 !important;
        box-shadow: 0 0 0 1px rgba(203, 213, 224, 0.3) !important;
    }
    
    .stButton > button {
        background-color: #f8f9fa;
        color: #4a5568;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.4rem 1.2rem;
        font-size: 0.85rem;
        font-weight: 400;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e0;
        color: #2d3748;
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(203, 213, 224, 0.3);
    }
    
    .timestamp {
        font-size: 0.75rem;
        color: #a0aec0;
        margin-top: 0.25rem;
    }
    
    .conversation-starters {
        margin-top: 2rem;
        padding: 1rem;
        background-color: #fafbfc;
        border-radius: 8px;
        border: 1px solid #f1f5f9;
    }
    
    .starter-title {
        font-size: 0.9rem;
        color: #718096;
        margin-bottom: 0.75rem;
        font-weight: 400;
    }
    
    .starter-button {
        display: block;
        width: 100%;
        text-align: left;
        padding: 0.6rem 0.8rem;
        margin: 0.3rem 0;
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: #4a5568;
        font-size: 0.85rem;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    
    .starter-button:hover {
        background-color: #f1f5f9;
    }
    
    /* Hide default streamlit elements */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'detected_mood' not in st.session_state:
        st.session_state.detected_mood = "neutral"

def detect_mood_from_text(text):
    """Simple mood detection from user's message"""
    text_lower = text.lower()
    
    # Mood indicators
    sad_words = ['sad', 'depressed', 'down', 'crying', 'hurt', 'pain', 'lost', 'empty', 'hopeless', 'broken']
    anxious_words = ['anxious', 'worried', 'nervous', 'panic', 'afraid', 'scared', 'overwhelmed', 'stress']
    happy_words = ['happy', 'excited', 'joy', 'great', 'amazing', 'wonderful', 'good', 'fantastic', 'love']
    frustrated_words = ['angry', 'frustrated', 'mad', 'annoyed', 'upset', 'irritated', 'hate']
    lonely_words = ['alone', 'lonely', 'isolated', 'nobody', 'empty', 'disconnected']
    
    # Count mood indicators
    mood_scores = {
        'sad': sum(1 for word in sad_words if word in text_lower),
        'anxious': sum(1 for word in anxious_words if word in text_lower),
        'happy': sum(1 for word in happy_words if word in text_lower),
        'frustrated': sum(1 for word in frustrated_words if word in text_lower),
        'lonely': sum(1 for word in lonely_words if word in text_lower)
    }
    
    # Detect strongest mood
    if max(mood_scores.values()) > 0:
        return max(mood_scores, key=mood_scores.get)
    
    return "neutral"

def get_empathetic_system_prompt(mood):
    """Create a system prompt based on detected mood"""
    base_prompt = """You are a gentle, empathetic companion focused on emotional support. Your responses should be:

- Naturally conversational and warm
- Validating of the person's feelings
- Supportive without being overwhelming
- Curious about their experience in a caring way
- Brief enough to feel like natural conversation
- Free of excessive enthusiasm or clinical language
- Short and understanding, sound like human

Keep responses concise (2-4 sentences typically) unless the person specifically needs more detailed support."""
    
    mood_contexts = {
        "sad": "The person seems to be experiencing sadness. Respond with gentle warmth and validation. Don't rush to fix or solve - sometimes people just need to be heard and understood.",
        "anxious": "The person appears anxious or worried. Offer calm, grounding presence. Help them feel heard and less alone with their concerns.",
        "happy": "The person seems happy or positive. Share in their energy naturally, but keep your warm, supportive nature.",
        "frustrated": "The person seems frustrated or upset. Acknowledge their feelings and provide a patient, understanding presence.",
        "lonely": "The person may be feeling isolated. Be a warm, caring presence and show genuine interest in their thoughts.",
        "neutral": "Respond with natural warmth and openness, ready to meet them wherever they are emotionally."
    }
    
    return base_prompt + f"\n\n{mood_contexts.get(mood, mood_contexts['neutral'])}"

def call_groq_api(messages, mood):
    """Call Groq API with empathetic prompting"""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        
        if not api_key:
            return "I'd love to chat with you, but I need to be properly connected first. Could you help set up the API key?"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Format messages with system prompt
        groq_messages = [{"role": "system", "content": get_empathetic_system_prompt(mood)}]
        for msg in messages[-10:]:  # Keep recent context
            groq_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": groq_messages,
            "max_tokens": 300,
            "temperature": 0.8,
            "top_p": 0.9
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "I'm having a moment of connection trouble, but I'm here with you. What's on your mind?"
            
    except Exception as e:
        return "I'm experiencing some technical hiccups, but I'm still here to listen. How are you doing?"

def main():
    initialize_session_state()
    
    # Simple, clean header
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🌸 Empaai</div>
        <div class="main-subtitle">A space for conversation</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display conversation history
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    {message["content"]}
                    <div class="timestamp">{message.get("timestamp", "")}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    {message["content"]}
                    <div class="timestamp">{message.get("timestamp", "")}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    user_input = st.text_area(
        label="",
        placeholder="What's on your mind?",
        height=80,
        key="user_input",
        label_visibility="collapsed"
    )

    # Use a form to capture Enter key press
    with st.form(key="chat_form", clear_on_submit=True):
        # Create invisible submit button that gets triggered by Enter
        submit_with_enter = st.form_submit_button("Send", type="primary", use_container_width=False)

    
    col1, col2, col3 = st.columns([1, 1, 3])

    
    with col1:
        send_clicked = st.button("Send", type="primary")
    
    with col2:
        if st.button("Clear"):
            st.session_state.messages = []
            st.session_state.detected_mood = "neutral"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle send button
    if send_clicked and user_input.strip():
        # Detect mood from user's message
        detected_mood = detect_mood_from_text(user_input)
        st.session_state.detected_mood = detected_mood
        
        # Add user message
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Get AI response
        with st.spinner(""):
            ai_response = call_groq_api(st.session_state.messages, detected_mood)
        
        # Add AI response
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        st.rerun()
    
    # Gentle conversation starters (only when no conversation exists)
    if not st.session_state.messages:
        st.markdown("""
        <div class="conversation-starters">
            <div class="starter-title">If you're not sure where to start...</div>
        </div>
        """, unsafe_allow_html=True)
        
        starters = [
            "I've been thinking about something lately",
            "How do I even begin to explain how I'm feeling?",
            "I had an interesting day today",
            "Something's been weighing on me",
            "I could use someone to talk to"
        ]
        
        for i, starter in enumerate(starters):
            if st.button(starter, key=f"starter_{i}"):
                # Detect mood and add message
                detected_mood = detect_mood_from_text(starter)
                st.session_state.detected_mood = detected_mood
                
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "user",
                    "content": starter,
                    "timestamp": timestamp
                })
                
                # Get AI response
                with st.spinner(""):
                    ai_response = call_groq_api(st.session_state.messages, detected_mood)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                st.rerun()

if __name__ == "__main__":
    main()
