import streamlit as st
import requests
import json
from datetime import datetime
import time
import os

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
    
    .api-selector {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_mood' not in st.session_state:
        st.session_state.user_mood = "neutral"
    if 'selected_api' not in st.session_state:
        st.session_state.selected_api = "huggingface"

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

def call_huggingface_api(messages, mood):
    """Call Hugging Face Inference API (FREE)"""
    try:
        # You can get a free API key from https://huggingface.co/settings/tokens
        api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
        
        if not api_key:
            return "Please add your free Hugging Face API key to use this service. Get one at: https://huggingface.co/settings/tokens"
        
        # Using Microsoft DialoGPT or similar model
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Format the conversation
        conversation_text = ""
        for msg in messages[-5:]:  # Last 5 messages for context
            role = "Human" if msg["role"] == "user" else "AI"
            conversation_text += f"{role}: {msg['content']}\n"
        
        # Add empathetic context
        system_context = get_empathetic_system_prompt(mood)
        full_prompt = f"{system_context}\n\n{conversation_text}AI:"
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Extract only the AI response
                if "AI:" in generated_text:
                    ai_response = generated_text.split("AI:")[-1].strip()
                    return ai_response if ai_response else "I'm here to listen. Could you tell me more about how you're feeling?"
            return "I understand you're reaching out. How can I support you today?"
        else:
            return f"I'm having trouble connecting right now. Let's try again in a moment."
            
    except Exception as e:
        return "I'm here for you, even if my connection isn't perfect right now. What would you like to talk about?"

def call_groq_api(messages, mood):
    """Call Groq API (FREE with higher limits)"""
    try:
        # Get free API key from https://console.groq.com/
        api_key = st.secrets.get("GROQ_API_KEY", "")
        
        if not api_key:
            return "Please add your free Groq API key to use this service. Get one at: https://console.groq.com/"
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Format messages
        groq_messages = [{"role": "system", "content": get_empathetic_system_prompt(mood)}]
        for msg in messages[-8:]:  # Last 8 messages for context
            groq_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": "llama3-8b-8192",  # Free model
            "messages": groq_messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return "I'm having some technical difficulties, but I'm still here to listen. What's on your mind?"
            
    except Exception as e:
        return "I'm experiencing some connection issues, but I want you to know I'm here for you. How are you feeling right now?"

def call_cohere_api(messages, mood):
    """Call Cohere API (FREE tier available)"""
    try:
        # Get free API key from https://dashboard.cohere.ai/
        api_key = st.secrets.get("COHERE_API_KEY", "")
        
        if not api_key:
            return "Please add your free Cohere API key to use this service. Get one at: https://dashboard.cohere.ai/"
        
        url = "https://api.cohere.ai/v1/generate"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Format conversation
        conversation_text = get_empathetic_system_prompt(mood) + "\n\n"
        for msg in messages[-6:]:  # Last 6 messages
            role = "Human" if msg["role"] == "user" else "AI Companion"
            conversation_text += f"{role}: {msg['content']}\n"
        conversation_text += "AI Companion:"
        
        payload = {
            "model": "command-light",  # Free model
            "prompt": conversation_text,
            "max_tokens": 300,
            "temperature": 0.7,
            "stop_sequences": ["Human:", "AI Companion:"]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["generations"][0]["text"].strip()
        else:
            return "I'm here to support you, even when technology isn't cooperating perfectly. What would you like to share?"
            
    except Exception as e:
        return "I'm experiencing some technical issues, but my care for your wellbeing remains constant. How can I help?"

def call_local_fallback(messages, mood):
    """Fallback empathetic responses when APIs aren't available"""
    fallback_responses = {
        "sad": [
            "I can hear that you're going through a difficult time right now. Your feelings are completely valid, and it's okay to feel sad. Sometimes we need to sit with these emotions before we can move through them. What's weighing most heavily on your heart?",
            "I'm sorry you're feeling this way. Sadness can feel overwhelming, but please know that you're not alone in this. Would you like to tell me more about what's happening?",
            "It sounds like you're carrying some heavy feelings right now. I want you to know that it's okay to not be okay. What's been the hardest part of your day?"
        ],
        "anxious": [
            "I can sense your anxiety, and I want you to know that what you're feeling is real and understandable. Let's take this one moment at a time. Can you tell me what's making you feel most anxious right now?",
            "Anxiety can make everything feel overwhelming. You're brave for reaching out. Let's focus on this moment - you're safe right now. What's going through your mind?",
            "I hear your worry, and I want to help you feel more grounded. Sometimes it helps to focus on what's within our control. What's causing you the most concern?"
        ],
        "stressed": [
            "It sounds like you're under a lot of pressure right now. Stress can make everything feel urgent and overwhelming. You're doing the best you can. What's been the biggest source of stress for you lately?",
            "I can feel the weight you're carrying. When we're stressed, it's easy to lose sight of our strength, but you're stronger than you know. What's been most challenging?",
            "Stress has a way of making everything feel impossible. But you've handled difficult things before, and you can handle this too. What's been most overwhelming for you?"
        ],
        "happy": [
            "I love hearing the joy in your message! It's wonderful when life gives us reasons to smile. I'd love to celebrate with you - what's brought you happiness today?",
            "Your happiness is contagious! It's beautiful to witness someone's joy. What's been the highlight of your day?",
            "There's something so special about genuine happiness. I'm so glad you're experiencing this joy. What's been making you feel so good?"
        ],
        "lonely": [
            "Loneliness can feel so heavy, and I want you to know that reaching out here shows incredible strength. You're not as alone as you might feel. What's been making you feel most isolated?",
            "I hear you, and I want you to know that your feelings matter. Loneliness is painful, but you've taken a step by connecting here. What's been on your mind?",
            "Feeling lonely is one of the most human experiences, and it's nothing to be ashamed of. I'm here with you right now. What would help you feel more connected?"
        ],
        "frustrated": [
            "I can feel your frustration, and it's completely understandable to feel this way when things aren't going as planned. Your feelings are valid. What's been most frustrating for you?",
            "Frustration can be so consuming, especially when we feel stuck or unheard. I'm here to listen without judgment. What's been bothering you most?",
            "It sounds like you're dealing with something really challenging. Frustration often comes from caring deeply about something. What's been getting under your skin?"
        ],
        "neutral": [
            "I'm here and ready to listen to whatever you'd like to share. Sometimes the most meaningful conversations start with simple check-ins. How has your day been treating you?",
            "Thank you for reaching out. There's something beautiful about taking a moment to connect, even when everything feels ordinary. What's on your mind today?",
            "I'm glad you're here. Sometimes we don't need to have big emotions to benefit from connection. What would you like to talk about?"
        ]
    }
    
    import random
    responses = fallback_responses.get(mood, fallback_responses["neutral"])
    return random.choice(responses)

def get_ai_response(messages, mood, api_choice):
    """Get AI response based on selected API"""
    if api_choice == "groq":
        return call_groq_api(messages, mood)
    elif api_choice == "cohere":
        return call_cohere_api(messages, mood)
    elif api_choice == "huggingface":
        return call_huggingface_api(messages, mood)
    else:
        return call_local_fallback(messages, mood)

def main():
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💙 Your Free Empathetic AI Companion</h1>
        <p>I'm here to listen, understand, and support you - completely free</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Selection
    st.markdown('<div class="api-selector">', unsafe_allow_html=True)
    st.subheader("🔧 Choose Your AI Engine (All Free!)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🚀 Groq (Best)", help="Fast and powerful - requires free API key"):
            st.session_state.selected_api = "groq"
    with col2:
        if st.button("🤗 Hugging Face", help="Good quality - requires free API key"):
            st.session_state.selected_api = "huggingface"
    with col3:
        if st.button("🧠 Cohere", help="Reliable - requires free API key"):
            st.session_state.selected_api = "cohere"
    with col4:
        if st.button("💝 No API Needed", help="Built-in empathetic responses - works immediately"):
            st.session_state.selected_api = "fallback"
    
    # API Info
    api_info = {
        "groq": "🚀 **Groq**: Fast LLaMA model - [Get free API key](https://console.groq.com/)",
        "huggingface": "🤗 **Hugging Face**: DialoGPT model - [Get free API key](https://huggingface.co/settings/tokens)",
        "cohere": "🧠 **Cohere**: Command model - [Get free API key](https://dashboard.cohere.ai/)",
        "fallback": "💝 **No API**: Built-in empathetic responses - Works immediately!"
    }
    
    st.markdown(f"**Currently using:** {api_info[st.session_state.selected_api]}")
    st.markdown('</div>', unsafe_allow_html=True)
    
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
                    ai_response = get_ai_response(
                        st.session_state.messages, 
                        st.session_state.user_mood,
                        st.session_state.selected_api
                    )
                
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
                    ai_response = get_ai_response(
                        st.session_state.messages, 
                        st.session_state.user_mood,
                        st.session_state.selected_api
                    )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                st.rerun()
    
    # Sidebar with resources and setup
    with st.sidebar:
        st.header("💙 Setup Guide")
        st.markdown("""
        **Free API Options:**
        
        1. **Groq (Recommended)** 🚀
           - Fastest and most powerful
           - [Get free key](https://console.groq.com/)
           - Add as `GROQ_API_KEY` in secrets
        
        2. **Hugging Face** 🤗
           - Good for conversations
           - [Get free key](https://huggingface.co/settings/tokens)
           - Add as `HUGGINGFACE_API_KEY`
        
        3. **Cohere** 🧠
           - Reliable responses
           - [Get free key](https://dashboard.cohere.ai/)
           - Add as `COHERE_API_KEY`
        
        4. **No API Needed** 💝
           - Works immediately
           - Built-in empathetic responses
        """)
        
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
