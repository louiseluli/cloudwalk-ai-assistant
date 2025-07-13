"""
CloudWalk AI Chatbot Engine
===========================
The intelligent core that powers conversations about CloudWalk's revolutionary payment solutions.
Built with love for merchants on Earth... and eventually other planets! 🚀
"""

import re
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid 
from enum import Enum
import streamlit as st
from loguru import logger

# Import the new, reliable model from Groq
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate

from src.config import config, brand
from src.language_manager import language_manager, LanguageDetectionResult
from src.knowledge_base import knowledge_base


class ConversationIntent(Enum):
    """Types of user intents we can detect"""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICING_QUESTION = "pricing_question"
    TECHNICAL_SUPPORT = "technical_support"
    COMPANY_INFO = "company_info"
    FEATURE_EXPLANATION = "feature_explanation"
    COMPARISON = "comparison"
    HOW_TO_START = "how_to_start"
    CONTACT_SALES = "contact_sales"
    GENERAL_CHAT = "general_chat"


class UserProfile(Enum):
    """User profiles for personalized responses"""
    NEW_MERCHANT = "new_merchant"
    EXISTING_CUSTOMER = "existing_customer"
    TECHNICAL_USER = "technical_user"
    INVESTOR = "investor"
    PARTNER = "partner"
    GENERAL = "general"


@dataclass
class ConversationContext:
    """Maintains conversation state and context"""
    session_id: str
    language: str = "en"
    user_profile: UserProfile = UserProfile.GENERAL
    current_product: Optional[str] = None
    conversation_history: List[Dict] = field(default_factory=list)
    detected_intents: List[ConversationIntent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)


class CloudWalkChatbot:
    """
    The main chatbot engine - CloudWalk's AI-powered assistant
    Helping merchants save money and grow their business! 💜
    """
    
    def __init__(self):
        """Initialize the CloudWalk chatbot with all its intelligence"""
        # Initialize components
        self.language_manager = language_manager
        self.knowledge_base = knowledge_base
        
        # Initialize LLM with CloudWalk personality
        self.llm = self._initialize_llm()
        
        # Intent patterns for detection
        self.intent_patterns = self._initialize_intent_patterns()
        
        logger.info("CloudWalk Chatbot initialized! Ready to revolutionize payments! 🚀")
    

    def _initialize_llm(self):
        """Initialize the Groq language model"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("GROQ_API_KEY is not set! Please add it to your .env file.")
            logger.error("GROQ_API_KEY not found.")
            return None

        logger.info("✅ Using fast and reliable Groq Llama3 model.")
        return ChatGroq(
            temperature=0.2,
            model_name="llama3-8b-8192",
            groq_api_key=api_key
        )
    
    def _initialize_intent_patterns(self) -> Dict[ConversationIntent, List[str]]:
        """Initialize patterns for intent detection"""
        # This function remains unchanged, defining your intent logic
        return {
            ConversationIntent.GREETING: [r'\b(hi|hello|hey|ola|olá|oi|hola)\b'],
            ConversationIntent.PRODUCT_INQUIRY: [r'\b(infinitepay|jim|stratus|product|produto)\b'],
            ConversationIntent.PRICING_QUESTION: [r'\b(price|fee|rate|taxa|preço|custo|quanto custa)\b'],
        }
    
    def detect_intent(self, user_input: str) -> List[ConversationIntent]:
        """Detect user intent from their message"""
        detected_intents = []
        input_lower = user_input.lower()
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    detected_intents.append(intent)
                    break
        if not detected_intents:
            detected_intents.append(ConversationIntent.GENERAL_CHAT)
        return detected_intents

    def build_system_prompt(self, context: ConversationContext) -> str:
        """Build a dynamic system prompt based on context"""
        # This function remains unchanged, defining your bot's personality
        return f"""You are CloudWalk's AI assistant - friendly, knowledgeable, and passionate about helping merchants succeed!
Your personality is warm and professional. You are enthusiastic about our mission to democratize payments.
Use only a few emojis appropriately to add warmth. Speak in {context.language}.

Key Products:
- InfinitePay: Brazil's revolutionary payment platform (0% Pix!).
- JIM: Instant payments for the US (1.99% - lowest in market!).
- STRATUS: Lightning-fast blockchain for global payments.
"""
    
    def search_knowledge(self, query: str, context: ConversationContext) -> List[Dict]:
        """Search knowledge base with context awareness"""
        # This function remains unchanged, handling your RAG logic
        return self.knowledge_base.search(
            query=query,
            n_results=3,
            filter_language=context.language if context.language != 'en' else None,
            filter_product=context.current_product
        )
    
    def generate_response(self, user_input: str, context: ConversationContext) -> Tuple[str, ConversationContext]:
        """Generate a response using the Groq LLM"""
        if not self.llm:
            return "The chatbot is not configured correctly. Missing API key.", context

        # 1. Detect language and intent
        lang_result = self.language_manager.detect_language(user_input)
        if lang_result.confidence > 0.6:
            context.language = lang_result.detected_language
        
        # 2. Search for relevant information
        knowledge_results = self.search_knowledge(user_input, context)
        knowledge_context = "\n".join([doc['content'] for doc in knowledge_results])

        # 3. Build the list of messages for the chat model
        messages = [
            SystemMessage(content=self.build_system_prompt(context)),
            SystemMessage(content=f"Use this information to answer the user's question:\n{knowledge_context}")
        ]
        # Add past messages from history
        for msg in context.conversation_history[-4:]: # Last 4 messages
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        # Add the current user question
        messages.append(HumanMessage(content=user_input))

        try:
            # 4. Get the response from the chat model
            response = self.llm.invoke(messages)
            response_text = response.content.strip()

            # 5. Update the conversation history
            context.conversation_history.append({'role': 'user', 'content': user_input})
            context.conversation_history.append({'role': 'assistant', 'content': response_text})
            context.last_interaction = datetime.now()
            
            return response_text, context
            
        except Exception as e:
            logger.error(f"Error generating response from Groq: {e}")
            return "I apologize, but I encountered an error. Please try again.", context
    
    def format_response_with_brand(self, response: str) -> str:
        """Add CloudWalk branding elements to response"""
        if "💜" not in response and "🚀" not in response:
            response += "\n\n💜 CloudWalk - Payments made simple!"
        return response

# Streamlit session state helpers (no changes needed here)
def init_chatbot_state():
    """Initialize chatbot in Streamlit session state"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = CloudWalkChatbot()
    
    if 'conversation_context' not in st.session_state:
        st.session_state.conversation_context = ConversationContext(
            session_id=str(uuid.uuid4())
        )
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []


# Export everything
__all__ = [
    'CloudWalkChatbot', 
    'ConversationContext', 
    'ConversationIntent',
    'UserProfile',
    'init_chatbot_state'
]