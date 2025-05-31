# Replace your input section with this code:

# Input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Use form to capture both button clicks and Enter key
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area(
        label="",
        placeholder="What's on your mind? (Press Enter to send)",
        height=80,
        key="user_input",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col2:
        send_clicked = st.form_submit_button("➤", type="primary", help="Send message")

st.markdown('</div>', unsafe_allow_html=True)

# Handle send button and Enter key
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
