"""
CloudWalk Chatbot Configuration Manager
======================================
Handles all configuration, environment variables, and constants.
"""

import os
import sys # THIS LINE FIXES THE CRASH
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)


@dataclass
class CloudWalkBrand:
    """CloudWalk brand configuration"""
    name: str = "CloudWalk"
    tagline: str = "Creating the best payment network on Earth. Then other planets."
    primary_color: str = "#7B3FF2"  # Purple
    secondary_color: str = "#2D3142"  # Dark blue-gray
    accent_color: str = "#FF006E"  # Pink
    
    # Product names
    products: Dict[str, str] = None
    
    def __post_init__(self):
        self.products = {
            "infinitepay": "InfinitePay - Brazilian payment platform",
            "jim": "JIM - Instant payments for the US",
            "stratus": "STRATUS - Blockchain for financial solutions"
        }


@dataclass
class ModelConfig:
    """AI Model configuration"""
    # LLM settings
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Response settings
    response_styles: Dict[str, Dict] = None
    
    def __post_init__(self):
        self.response_styles = {
            "professional": {
                "temperature": 0.3,
                "system_prompt": "You are a professional CloudWalk representative."
            },
            "friendly": {
                "temperature": 0.7,
                "system_prompt": "You are a friendly CloudWalk assistant, warm and helpful."
            },
            "technical": {
                "temperature": 0.2,
                "system_prompt": "You are a technical CloudWalk expert, precise and detailed."
            }
        }


@dataclass
class ChatbotConfig:
    """Main chatbot configuration"""
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # App settings
    app_name: str = os.getenv("APP_NAME", "CloudWalk AI Assistant")
    app_version: str = os.getenv("APP_VERSION", "2.0.0")
    environment: str = os.getenv("APP_ENVIRONMENT", "development")
    
    # Language settings
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "en")
    supported_languages: List[str] = None
    
    # Features
    enable_memory: bool = True
    enable_multilingual: bool = True
    enable_analytics: bool = True
    enable_voice: bool = False  # Future feature
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __post_init__(self):
        # Parse supported languages
        languages = os.getenv("SUPPORTED_LANGUAGES", "en,pt-BR")
        self.supported_languages = [lang.strip() for lang in languages.split(",")]
        
        # Configure logging to be quiet in the terminal
        logger.remove() # Remove default console logger
        logger.add(
            sys.stderr, level="ERROR" # Only show errors in the console
        )
        logger.add(
            LOGS_DIR / "chatbot_{time}.log",
            rotation="1 day",
            retention="7 days",
            level=self.log_level # Log everything to the file
        )
        
        # Validate API key
        if not self.openai_api_key and self.environment == "production":
            raise ValueError("OpenAI API key is required in production!")


# Singleton instances
config = ChatbotConfig()
brand = CloudWalkBrand()
model_config = ModelConfig()

# CloudWalk Knowledge Base Structure
KNOWLEDGE_CATEGORIES = {
    "company": {
        "mission": "Create the best payment network on Earth",
        "values": ["Innovation", "Customer Focus", "Disruptive Economics"],
        "culture": "AI-driven, customer-centric, innovative"
    },
    "products": {
        "infinitepay": {
            "description": "Powerful financial platform for Brazilian businesses",
            "features": ["Low fees", "Instant payments", "No monthly charges"],
            "target": "Brazilian merchants"
        },
        "jim": {
            "description": "Instant payment meets AI magic in the US",
            "features": ["1.99% per transaction", "No hardware needed", "AI assistant"],
            "target": "US merchants"
        },
        "stratus": {
            "description": "High-performance blockchain for payments",
            "features": ["1,800 TPS", "Open source", "Scalable"],
            "target": "Global payment networks"
        }
    },
    "technology": {
        "ai_capabilities": [
            "Fraud detection",
            "Credit assessment", 
            "Customer support automation",
            "Behavioral analysis"
        ],
        "infrastructure": "Cloud-native, scalable, secure"
    }
}

# Export all configurations
__all__ = ['config', 'brand', 'model_config', 'KNOWLEDGE_CATEGORIES', 
           'PROJECT_ROOT', 'DATA_DIR', 'LOGS_DIR']