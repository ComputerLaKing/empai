import streamlit as st
import anthropic
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="Empathetic AI Companion",
    page_icon="💙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a warm, welcoming interface
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
    }
    
    .ai-message {
        background-color: #e8f4f8;
        border-left-color: #4ecdc4;
    }
    
    .mood-selector {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_mood' not in st.session_state:
        st.session_state.user_mood = "neutral"
    if 'conversation_context' not in st.session_state:
        st.session_state.conversation_context = ""

def get_empathetic_system_prompt(mood):
    """Create a system prompt based on user's current mood"""
    base_prompt = """You are an empathetic AI companion designed to provide emotional support and understanding. Your role is to:

1. Listen actively and validate the user's feelings
2. Respond with warmth, compassion, and understanding
3. Offer gentle guidance when appropriate, but never be preachy
4. Ask thoughtful follow-up questions to show genuine interest
5. Remember context from the conversation to build rapport
6. Use a conversational, supportive tone
7. Acknowledge emotions without trying to "fix" everything immediately

"""
    
    mood_contexts = {
        "sad": "The user is feeling sad. Be extra gentle, validate their feelings, and offer comfort. Don't rush to solutions - sometimes people just need to be heard.",
        "anxious": "The user is feeling anxious. Be calming and reassuring. Help them feel grounded. Offer practical coping strategies if appropriate.",
        "stressed": "The user is feeling stressed. Be understanding and supportive. Help them feel less overwhelmed. Ask about what's causing stress.",
        "happy": "The user is feeling happy. Share in their joy! Be enthusiastic and positive while maintaining your supportive nature.",
        "lonely": "The user is feeling lonely. Be a warm, caring presence. Show genuine interest in their thoughts and experiences.",
        "frustrated": "The user is feeling frustrated. Validate their frustration and be patient. Help them feel heard and understood.",
        "neutral": "The user's mood is neutral. Be warm and approachable, ready to adapt to whatever they need to discuss."
    }
    
    return base_prompt + f"\nCurrent context: {mood_contexts.get(mood, mood_contexts['neutral'])}"

def call_claude_api(messages, mood):
    """Call Claude API with empathetic prompting"""
    try:
        # Get API key from secrets
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        client = anthropic.Anthropic(api_key=api_key)
        
        # Prepare messages with system prompt
        system_prompt = get_empathetic_system_prompt(mood)
        
        # Format conversation history
        claude_messages = []
        for msg in messages:
            claude_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=claude_messages
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"I'm sorry, I'm having trouble connecting right now. Error: {str(e)}"

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💙 Your Empathetic AI Companion</h1>
        <p>I'm here to listen, understand, and support you</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mood selector
    st.markdown('<div class="mood-selector">', unsafe_allow_html=True)
    st.subheader("How are you feeling right now?")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("😢 Sad"):
            st.session_state.user_mood = "sad"
        if st.button("😰 Anxious"):
            st.session_state.user_mood = "anxious"
    
    with col2:
        if st.button("😤 Stressed"):
            st.session_state.user_mood = "stressed"
        if st.button("😊 Happy"):
            st.session_state.user_mood = "happy"
    
    with col3:
        if st.button("😔 Lonely"):
            st.session_state.user_mood = "lonely"
        if st.button("😠 Frustrated"):
            st.session_state.user_mood = "frustrated"
    
    with col4:
        if st.button("😐 Neutral"):
            st.session_state.user_mood = "neutral"
        if st.button("🤗 Just want to chat"):
            st.session_state.user_mood = "neutral"
    
    st.markdown(f"**Current mood:** {st.session_state.user_mood.title()}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display conversation history
    if st.session_state.messages:
        st.subheader("Our conversation")
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                    <small style="color: #666; float: right;">{message.get("timestamp", "")}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>AI Companion:</strong> {message["content"]}
                    <small style="color: #666; float: right;">{message.get("timestamp", "")}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.subheader("Share what's on your mind")
    user_input = st.text_area(
        "I'm here to listen...",
        placeholder="Tell me what's happening, how you're feeling, or what's on your mind. There's no judgment here - just understanding.",
        height=100,
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💬 Send", type="primary"):
            if user_input.strip():
                # Add user message
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": timestamp
                })
                
                # Get AI response
                with st.spinner("Thinking with care..."):
                    ai_response = call_claude_api(st.session_state.messages, st.session_state.user_mood)
                
                # Add AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                # Clear input and rerun
                st.rerun()
    
    with col2:
        if st.button("🔄 New Conversation"):
            st.session_state.messages = []
            st.session_state.user_mood = "neutral"
            st.rerun()
    
    # Quick conversation starters
    if not st.session_state.messages:
        st.subheader("Not sure where to start?")
        st.markdown("Here are some conversation starters:")
        
        starters = [
            "I'm having a rough day and need someone to talk to",
            "I'm feeling overwhelmed with everything going on",
            "I accomplished something today and want to share",
            "I'm worried about something and need to process it",
            "I just need someone to listen without judgment"
        ]
        
        for starter in starters:
            if st.button(f"💭 {starter}", key=starter):
                st.session_state.messages.append({
                    "role": "user",
                    "content": starter,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                with st.spinner("Thinking with care..."):
                    ai_response = call_claude_api(st.session_state.messages, st.session_state.user_mood)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                st.rerun()
    
    # Sidebar with resources
    with st.sidebar:
        st.header("💙 Support Resources")
        st.markdown("""
        **Remember:**
        - This AI companion is here to listen and support
        - For crisis situations, please contact professional help
        - You deserve care and understanding
        
        **Crisis Resources:**
        - National Suicide Prevention Lifeline: 988
        - Crisis Text Line: Text HOME to 741741
        - International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/
        """)
        
        st.header("🛠️ Conversation Tools")
        if st.button("📥 Export Conversation"):
            if st.session_state.messages:
                conversation_text = ""
                for msg in st.session_state.messages:
                    role = "You" if msg["role"] == "user" else "AI Companion"
                    conversation_text += f"{role} ({msg.get('timestamp', '')}): {msg['content']}\n\n"
                
                st.download_button(
                    label="Download as Text File",
                    data=conversation_text,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
