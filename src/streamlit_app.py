"""
CloudWalk AI Assistant - Streamlit Interface
===========================================
A beautiful, modern chat interface for CloudWalk's revolutionary payment solutions.
Built with 💜 for merchants everywhere!
"""

import streamlit as st
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.config import config, brand
from src.chatbot_engine import CloudWalkChatbot, ConversationContext, init_chatbot_state
from src.language_manager import language_manager, init_language_state
from loguru import logger


# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="CloudWalk AI Assistant",
    page_icon="🚀",
    layout="centered", # Use centered layout for a cleaner chat look
    initial_sidebar_state="expanded",
    menu_items={
        'About': "CloudWalk - Creating the best payment network on Earth. Then other planets! 🚀"
    }
)

def load_custom_css():
    """Load the final, polished CSS for the app"""
    st.markdown(f"""
    <style>
    /* Import a clean, modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

    /* Brand Colors */
    :root {{
        --purple: {brand.primary_color};
        --dark-bg: #13111C;
        --light-bg: #F5F5F7;
        --text-dark: #212529;
        --text-light: #F8F9FA;
        --border-color: #E9ECEF;
    }}

    /* General Body Styling */
    body {{
        font-family: 'Inter', sans-serif;
        color: var(--text-dark);
    }}

    /* Main chat container */
    [data-testid="main"] {{
        background-color: var(--light-bg);
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: var(--dark-bg);
        border-right: 1px solid var(--border-color);
    }}
    [data-testid="stSidebar"] * {{
        color: var(--text-light);
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background-color: var(--purple);
        border-color: var(--purple);
    }}
    [data-testid="stSidebar"] .stMetric {{
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 10px;
    }}

    /* Chat Bubble Styling */
    .user-message-container, .assistant-message-container {{
        display: flex;
        width: 100%;
        margin-bottom: 1rem;
    }}
    
    .user-message-container {{
        justify-content: flex-end;
    }}
    
    .assistant-message-container {{
        justify-content: flex-start;
        align-items: flex-start;
    }}
    
    .chat-bubble {{
        max-width: 85%;
        padding: 0.8rem 1.2rem;
        border-radius: 18px;
        line-height: 1.6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    
    .user-bubble {{
        background-color: var(--purple);
        color: var(--text-light);
        border-bottom-right-radius: 4px;
    }}

    .assistant-bubble {{
        background-color: #FFFFFF;
        color: var(--text-dark);
        border: 1px solid var(--border-color);
        border-bottom-left-radius: 4px;
    }}
    
    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.5rem;
        background-color: #FFFFFF;
        border: 1px solid var(--border-color);
        margin-right: 12px;
    }}

    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with options, info, and metrics"""
    with st.sidebar:
        st.markdown(f"# 💜 {brand.name}")
        st.markdown("---")
        
        # Language selector
        languages = {'en': '🇺🇸 English', 'pt-BR': '🇧🇷 Português'}
        selected_lang = st.selectbox(
            "Language / Idioma",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            key='language_selector'
        )
        if selected_lang != st.session_state.get('language'):
            st.session_state.language = selected_lang
            language_manager.set_language(selected_lang)
            # No rerun needed, will be picked up on next interaction
        
        st.markdown("---")

        # Session Info (Moved from footer)
        with st.expander("📊 Session Info", expanded=True):
            messages_count = len(st.session_state.get('messages', []))
            st.metric("💬 Messages Exchanged", messages_count)
            
            product_focus = st.session_state.conversation_context.current_product or "None"
            st.metric("🛍️ Product Focus", product_focus.capitalize())

        st.markdown("---")
        
        # Products
        with st.expander("🚀 Our Products", expanded=True):
            st.markdown(f"**InfinitePay:** {brand.products['infinitepay']}")
            st.markdown(f"**JIM:** {brand.products['jim']}")
            st.markdown(f"**STRATUS:** {brand.products['stratus']}")
        
        st.markdown("---")
        
        st.info("This is an AI assistant. Information may not always be 100% accurate.")


def main():
    """Main Streamlit application"""
    # Initialize state and CSS
    init_chatbot_state()
    init_language_state()
    load_custom_css()
    
    render_sidebar()
    
    # Header in the main panel
    st.markdown("## CloudWalk AI Assistant")

    # Render chat history
    for message in st.session_state.get('messages', []):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message-container">
                <div class="chat-bubble user-bubble">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message-container">
                <div class="avatar">🤖</div>
                <div class="chat-bubble assistant-bubble">
                    {message["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Chat input, which is now correctly placed at the bottom
    if prompt := st.chat_input("Ask me about CloudWalk..."):
        # Add user message to state and history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Immediately display user message
        st.rerun()

    # Generate AI response if the last message was from the user
    if st.session_state.get('messages') and st.session_state.messages[-1]["role"] == "user":
        user_prompt = st.session_state.messages[-1]["content"]
        
        with st.spinner("CloudWalk AI is thinking... 🧠"):
            response_text, updated_context = st.session_state.chatbot.generate_response(
                user_prompt,
                st.session_state.conversation_context
            )
            final_response = st.session_state.chatbot.format_response_with_brand(response_text)
            st.session_state.conversation_context = updated_context

        # Add assistant response to state and display
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        st.rerun()

    # Welcome message for new chats
    if not st.session_state.get('messages', []):
        st.info("Welcome! How can I help you learn about CloudWalk's payment solutions today?")


# Run the app
if __name__ == "__main__":
    main()