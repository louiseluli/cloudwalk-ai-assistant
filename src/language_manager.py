"""
CloudWalk Language Detection and Multi-lingual Support
=====================================================
Handles language detection, translation, and localized responses.
"""

import re
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from loguru import logger
import streamlit as st

# Language detection patterns
LANGUAGE_PATTERNS = {
    'pt-BR': {
        'patterns': [
            r'\b(olá|oi|bom dia|boa tarde|boa noite|obrigad[oa]|por favor|tchau|até|vocês?|está|estou|são|sou|meu|minha|nosso|nossa)\b',
            r'\b(maquininha|cartão|pagamento|taxa|pix|boleto|conta|dinheiro|receber|vender|comprar)\b',
            r'\b(fazer|querer|poder|precisar|ter|ser|estar)\b',
            r'\b(não|sim|talvez|claro|certo|errado)\b'
        ],
        'stop_words': ['de', 'da', 'do', 'a', 'o', 'um', 'uma', 'para', 'com', 'em', 'no', 'na'],
        'greeting_responses': [
            "Olá! Bem-vindo à CloudWalk! 🚀",
            "Oi! Como posso ajudar você hoje?",
            "Seja bem-vindo! Sou o assistente da CloudWalk."
        ]
    },
    'en': {
        'patterns': [
            r'\b(hello|hi|good morning|good afternoon|good evening|thanks|thank you|please|bye|goodbye|you|your|are|am|is|my|our)\b',
            r'\b(card|payment|fee|rate|account|money|receive|sell|buy|terminal)\b',
            r'\b(do|want|can|need|have|be)\b',
            r'\b(no|yes|maybe|sure|right|wrong)\b'
        ],
        'stop_words': ['the', 'a', 'an', 'to', 'for', 'with', 'in', 'on', 'at'],
        'greeting_responses': [
            "Hello! Welcome to CloudWalk! 🚀",
            "Hi there! How can I help you today?",
            "Welcome! I'm CloudWalk's AI assistant."
        ]
    }
}

# Localized content
LOCALIZED_CONTENT = {
    'pt-BR': {
        'company_intro': "A CloudWalk está revolucionando o mercado de pagamentos no Brasil com a InfinitePay!",
        'products': {
            'infinitepay': "InfinitePay - A maquininha que está transformando negócios brasileiros",
            'jim': "JIM - Nossa solução de pagamentos instantâneos para os EUA",
            'stratus': "STRATUS - Blockchain de alta performance para soluções financeiras"
        },
        'common_questions': {
            'fees': "Nossas taxas começam em 0% no Pix, 0.75% no débito e 2.69% no crédito à vista!",
            'support': "Temos suporte RA1000 - o melhor do Brasil!",
            'how_it_works': "É simples: você vende, recebe na hora ou em 1 dia útil, com as menores taxas!"
        },
        'cta': "Quer saber mais? Posso explicar sobre nossas maquininhas, taxas ou qualquer dúvida!"
    },
    'en': {
        'company_intro': "CloudWalk is revolutionizing payments globally with AI-powered solutions!",
        'products': {
            'infinitepay': "InfinitePay - Brazil's game-changing payment platform",
            'jim': "JIM - Instant payments meet AI magic in the US",
            'stratus': "STRATUS - High-performance blockchain for financial solutions"
        },
        'common_questions': {
            'fees': "Our fees start at 0% for Pix, 0.75% for debit, and 2.69% for credit!",
            'support': "We have RA1000-rated support - Brazil's best!",
            'how_it_works': "It's simple: sell, get paid instantly or next day, lowest fees!"
        },
        'cta': "Want to know more? Ask me about our products, fees, or anything else!"
    }
}


@dataclass
class LanguageDetectionResult:
    """Results from language detection"""
    detected_language: str
    confidence: float
    alternative_language: Optional[str] = None
    alternative_confidence: Optional[float] = None


class LanguageManager:
    """Manages language detection and localization for CloudWalk chatbot"""
    
    def __init__(self, default_language: str = 'en'):
        self.default_language = default_language
        self.current_language = default_language
        self.language_history: List[str] = []
        
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect language using pattern matching and frequency analysis
        
        Args:
            text: User input text
            
        Returns:
            LanguageDetectionResult with detected language and confidence
        """
        text_lower = text.lower()
        scores = {}
        
        # Calculate scores for each language
        for lang, config in LANGUAGE_PATTERNS.items():
            score = 0
            matches = 0
            
            # Check patterns
            for pattern in config['patterns']:
                pattern_matches = len(re.findall(pattern, text_lower))
                matches += pattern_matches
                score += pattern_matches * 2  # Weight pattern matches higher
            
            # Check stop words
            words = text_lower.split()
            stop_word_matches = sum(1 for word in words if word in config['stop_words'])
            score += stop_word_matches
            
            # Normalize by text length
            if len(words) > 0:
                scores[lang] = score / len(words)
            else:
                scores[lang] = 0
                
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_scores or sorted_scores[0][1] == 0:
            # No clear detection, use default
            return LanguageDetectionResult(
                detected_language=self.default_language,
                confidence=0.0
            )
        
        # Calculate confidence
        top_lang, top_score = sorted_scores[0]
        confidence = min(top_score / 0.5, 1.0)  # Normalize confidence
        
        result = LanguageDetectionResult(
            detected_language=top_lang,
            confidence=confidence
        )
        
        # Add alternative if close
        if len(sorted_scores) > 1 and sorted_scores[1][1] > 0:
            alt_lang, alt_score = sorted_scores[1]
            if alt_score / top_score > 0.7:  # Within 70% of top score
                result.alternative_language = alt_lang
                result.alternative_confidence = min(alt_score / 0.5, 1.0)
        
        logger.debug(f"Language detection: {result}")
        return result
    
    def get_greeting(self, language: str) -> str:
        """Get a localized greeting"""
        import random
        greetings = LANGUAGE_PATTERNS.get(language, LANGUAGE_PATTERNS['en'])['greeting_responses']
        return random.choice(greetings)
    
    def get_localized_content(self, key: str, language: Optional[str] = None) -> str:
        """
        Get localized content by key
        
        Args:
            key: Content key (e.g., 'company_intro', 'products.infinitepay')
            language: Language code, uses current if not specified
            
        Returns:
            Localized content string
        """
        if language is None:
            language = self.current_language
            
        content = LOCALIZED_CONTENT.get(language, LOCALIZED_CONTENT['en'])
        
        # Navigate nested keys
        keys = key.split('.')
        for k in keys:
            if isinstance(content, dict):
                content = content.get(k, f"[Missing: {key}]")
            else:
                break
                
        return content
    
    def set_language(self, language: str) -> None:
        """Set the current language"""
        if language in LANGUAGE_PATTERNS:
            self.current_language = language
            self.language_history.append(language)
            logger.info(f"Language set to: {language}")
    
    def translate_product_name(self, product: str, to_language: Optional[str] = None) -> str:
        """Translate product names consistently"""
        if to_language is None:
            to_language = self.current_language
            
        # Product names generally stay the same, but we can add context
        translations = {
            'infinitepay': {
                'pt-BR': 'InfinitePay',
                'es': 'InfinitePay',
                'en': 'InfinitePay'
            },
            'jim': {
                'pt-BR': 'JIM (para os EUA)',
                'es': 'JIM (para EEUU)',
                'en': 'JIM'
            },
            'stratus': {
                'pt-BR': 'STRATUS (Blockchain)',
                'es': 'STRATUS (Blockchain)',
                'en': 'STRATUS'
            }
        }
        
        product_lower = product.lower()
        if product_lower in translations:
            return translations[product_lower].get(to_language, product)
        return product
    
    def format_currency(self, amount: float, currency: str = 'BRL', language: Optional[str] = None) -> str:
        """Format currency according to language/locale"""
        if language is None:
            language = self.current_language
            
        formatters = {
            'pt-BR': {
                'BRL': lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'USD': lambda x: f"US$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            },
            'es': {
                'BRL': lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'USD': lambda x: f"US$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            },
            'en': {
                'BRL': lambda x: f"R$ {x:,.2f}",
                'USD': lambda x: f"${x:,.2f}"
            }
        }
        
        formatter = formatters.get(language, formatters['en']).get(currency, lambda x: f"{currency} {x:,.2f}")
        return formatter(amount)
    
    def get_language_emoji(self, language: str) -> str:
        """Get flag emoji for language"""
        flags = {
            'pt-BR': '🇧🇷',
            'es': '🌎',  # Generic for Latin America
            'en': '🇺🇸'
        }
        return flags.get(language, '🌍')


# Singleton instance
language_manager = LanguageManager()

# Streamlit session state helper
def init_language_state():
    """Initialize language in Streamlit session state"""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'language_manager' not in st.session_state:
        st.session_state.language_manager = language_manager


# Export
__all__ = ['LanguageManager', 'language_manager', 'LanguageDetectionResult', 
          'LOCALIZED_CONTENT', 'init_language_state']