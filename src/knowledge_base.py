"""
CloudWalk Knowledge Base Manager
================================
Manages all CloudWalk information, products, and documentation.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import pandas as pd
from loguru import logger
import chromadb
from chromadb.config import Settings
import hashlib

from src.config import DATA_DIR, brand, KNOWLEDGE_CATEGORIES


@dataclass
class KnowledgeDocument:
    """Represents a piece of knowledge in our base"""
    id: str
    title: str
    content: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    language: str = 'en'
    product: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'subcategory': self.subcategory,
            'tags': self.tags,
            'language': self.language,
            'product': self.product,
            'last_updated': self.last_updated.isoformat(),
            'metadata': self.metadata
        }


class CloudWalkKnowledgeBase:
    """Manages CloudWalk's knowledge base with vector search"""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """Initialize knowledge base with ChromaDB"""
        self.persist_directory = persist_directory or DATA_DIR / "knowledge_base"
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="cloudwalk_knowledge",
            metadata={"description": "CloudWalk products and company information"}
        )
        
        # Initialize with core knowledge
        self._initialize_core_knowledge()
        
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _initialize_core_knowledge(self):
        """Load core CloudWalk knowledge into the base"""
        core_documents = [
            # Company Information
            KnowledgeDocument(
                id=self._generate_id("cloudwalk_mission"),
                title="CloudWalk Mission",
                content="Our mission is to create the best payment network on Earth. Then other planets. We are democratizing the financial industry, empowering entrepreneurs through technological, inclusive and life-changing solutions.",
                category="company",
                subcategory="mission",
                tags=["mission", "vision", "company", "about"],
                language="en"
            ),
            
            # InfinitePay - Brazilian Product
            KnowledgeDocument(
                id=self._generate_id("infinitepay_overview"),
                title="InfinitePay Overview",
                content="InfinitePay is a powerful financial platform democratizing access to world-class payment products and software, currently serving millions of clients in Brazil. Launched in 2019, it represented the most disruptive wave of innovation in the Brazilian payments industry.",
                category="products",
                subcategory="infinitepay",
                tags=["infinitepay", "brazil", "payments", "maquininha"],
                language="en",
                product="infinitepay"
            ),
            
            KnowledgeDocument(
                id=self._generate_id("infinitepay_fees"),
                title="InfinitePay Fees",
                content="InfinitePay offers the lowest fees in Brazil: 0.00% for Pix, 0.75% for Debit, 2.69% for Credit (1x), and 8.99% for Credit (12x). These are final rates including anticipation. No monthly fees or hidden costs.",
                category="products",
                subcategory="fees",
                tags=["fees", "rates", "pricing", "costs", "infinitepay"],
                language="en",
                product="infinitepay"
            ),
            
            KnowledgeDocument(
                id=self._generate_id("infinitepay_maquininha"),
                title="InfinitePay Maquininha Smart",
                content="The Maquininha Smart is available for just 12x R$ 16.58 or R$ 199. It includes: Pix with zero fees, receipt printing, long battery life, inventory management, free shipping, and no rental fees or loyalty requirements.",
                category="products",
                subcategory="hardware",
                tags=["maquininha", "hardware", "terminal", "pos", "infinitepay"],
                language="en",
                product="infinitepay"
            ),
            
            KnowledgeDocument(
                id=self._generate_id("infinitetap_overview"),
                title="InfiniteTap - Phone as Card Reader",
                content="InfiniteTap transforms your smartphone into a card reader in less than 5 minutes. Works on Android and iOS with NFC. Zero investment required, accepts payments up to 12x installments.",
                category="products",
                subcategory="infinitetap",
                tags=["tap", "nfc", "mobile", "smartphone", "infinitepay"],
                language="en",
                product="infinitepay"
            ),
            
            # JIM - US Product
            KnowledgeDocument(
                id=self._generate_id("jim_overview"),
                title="JIM Overview",
                content="JIM brings the power of instant payments for everyone in the US. Combining cutting edge technology with unparalleled design, JIM enables sellers to accept payments, receive money instantly, and access a next generation AI assistant.",
                category="products",
                subcategory="jim",
                tags=["jim", "usa", "instant", "payments"],
                language="en",
                product="jim"
            ),
            
            KnowledgeDocument(
                id=self._generate_id("jim_features"),
                title="JIM Features and Pricing",
                content="JIM offers: 1.99% per transaction (lowest in market), instant payouts in seconds, no hardware needed (phone only), accepts all major cards and digital wallets, AI-powered business insights. No hidden fees, no monthly charges.",
                category="products",
                subcategory="features",
                tags=["jim", "fees", "instant", "mobile", "ai"],
                language="en",
                product="jim"
            ),
            
            # STRATUS - Blockchain
            KnowledgeDocument(
                id=self._generate_id("stratus_overview"),
                title="STRATUS Blockchain",
                content="STRATUS is a high performance, secure, scalable, and open-source blockchain designed for global payment networks. It processes up to 1,800 transactions per second (TPS) with potential for infinite growth through sharding and multi-raft consensus models.",
                category="products",
                subcategory="stratus",
                tags=["stratus", "blockchain", "technology", "infrastructure"],
                language="en",
                product="stratus"
            ),
            
            # AI and Technology
            KnowledgeDocument(
                id=self._generate_id("cloudwalk_ai"),
                title="CloudWalk AI Capabilities",
                content="CloudWalk leverages AI across multiple fronts: fraud detection with 3-layer system (transactional, behavioral, relational), credit assessment using actual behavior data, customer support automation handling substantial chats without human intervention, and merchant vector space for business analysis.",
                category="technology",
                subcategory="ai",
                tags=["ai", "ml", "fraud", "credit", "automation"],
                language="en"
            ),
            
            # Support and Values
            KnowledgeDocument(
                id=self._generate_id("cloudwalk_support"),
                title="CloudWalk Support Excellence",
                content="CloudWalk provides RA1000-rated support, the highest quality rating in Brazil. Our support team is always ready to help with questions and resolve problems quickly and efficiently.",
                category="support",
                subcategory="customer_service",
                tags=["support", "ra1000", "help", "service"],
                language="en"
            ),
            
            # Portuguese content
            KnowledgeDocument(
                id=self._generate_id("infinitepay_overview_pt"),
                title="Visão Geral InfinitePay",
                content="InfinitePay é uma poderosa plataforma financeira democratizando o acesso a produtos de pagamento de classe mundial, atualmente atendendo milhões de clientes no Brasil. Lançada em 2019, representou a onda mais disruptiva de inovação no setor de pagamentos brasileiro.",
                category="products",
                subcategory="infinitepay",
                tags=["infinitepay", "brasil", "pagamentos", "maquininha"],
                language="pt-BR",
                product="infinitepay"
            ),
            
            KnowledgeDocument(
                id=self._generate_id("infinitepay_taxas_pt"),
                title="Taxas InfinitePay",
                content="InfinitePay oferece as menores taxas do Brasil: 0,00% no Pix, 0,75% no Débito, 2,69% no Crédito à vista, e 8,99% no Crédito 12x. São taxas finais já com antecipação. Sem mensalidade ou custos escondidos.",
                category="products",
                subcategory="fees",
                tags=["taxas", "preços", "custos", "infinitepay"],
                language="pt-BR",
                product="infinitepay"
            )
        ]
        
        # Add documents to collection if not already present
        existing_ids = set()
        try:
            results = self.collection.get()
            if results and 'ids' in results:
                existing_ids = set(results['ids'])
        except Exception as e:
            logger.warning(f"Could not check existing documents: {e}")
        
        new_documents = [doc for doc in core_documents if doc.id not in existing_ids]
        
        if new_documents:
            self._add_documents(new_documents)
            logger.info(f"Added {len(new_documents)} new core documents to knowledge base")
    
    def _add_documents(self, documents: List[KnowledgeDocument]):
        """Add documents to the collection"""
        if not documents:
            return
            
        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [
            {
                'title': doc.title,
                'category': doc.category,
                'subcategory': doc.subcategory or '',
                'tags': ','.join(doc.tags),
                'language': doc.language,
                'product': doc.product or '',
                'last_updated': doc.last_updated.isoformat()
            }
            for doc in documents
        ]
        
        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )
    
    def search(self, 
              query: str, 
              n_results: int = 5,
              filter_language: Optional[str] = None,
              filter_product: Optional[str] = None,
              filter_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search knowledge base with filters
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_language: Filter by language
            filter_product: Filter by product
            filter_category: Filter by category
            
        Returns:
            List of relevant documents with scores
        """
        # Build where clause for filters
        where = {}
        if filter_language:
            where['language'] = filter_language
        if filter_product:
            where['product'] = filter_product
        if filter_category:
            where['category'] = filter_category
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None
        )
        
        # Format results
        formatted_results = []
        if results and 'ids' in results and results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_by_category(self, category: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all documents in a category"""
        where = {'category': category}
        if language:
            where['language'] = language
            
        results = self.collection.get(where=where)
        
        formatted_results = []
        if results and 'ids' in results:
            for i in range(len(results['ids'])):
                formatted_results.append({
                    'id': results['ids'][i],
                    'content': results['documents'][i],
                    'metadata': results['metadatas'][i]
                })
        
        return formatted_results
    
    def get_product_info(self, product: str, language: str = 'en') -> Dict[str, Any]:
        """Get comprehensive information about a product"""
        results = self.search(
            query=product,
            filter_product=product.lower(),
            filter_language=language,
            n_results=10
        )
        
        # Organize by subcategory
        info = {
            'overview': '',
            'features': '',
            'pricing': '',
            'other': []
        }
        
        for result in results:
            metadata = result['metadata']
            subcategory = metadata.get('subcategory', '')
            
            if 'overview' in subcategory or 'overview' in metadata.get('title', '').lower():
                info['overview'] = result['content']
            elif 'feature' in subcategory or 'feature' in metadata.get('title', '').lower():
                info['features'] = result['content']
            elif 'fee' in subcategory or 'pricing' in subcategory or 'taxa' in subcategory:
                info['pricing'] = result['content']
            else:
                info['other'].append(result['content'])
        
        return info
    
    def add_custom_knowledge(self, 
                           title: str,
                           content: str,
                           category: str,
                           tags: List[str],
                           language: str = 'en',
                           **kwargs) -> str:
        """Add custom knowledge to the base"""
        doc_id = self._generate_id(f"{title}_{content}")
        
        document = KnowledgeDocument(
            id=doc_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            language=language,
            **kwargs
        )
        
        self._add_documents([document])
        logger.info(f"Added custom knowledge: {title}")
        
        return doc_id


# Singleton instance
knowledge_base = CloudWalkKnowledgeBase()

# Export
__all__ = ['CloudWalkKnowledgeBase', 'knowledge_base', 'KnowledgeDocument']