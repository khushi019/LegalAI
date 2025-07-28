import os
import sys
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers.pipelines import pipeline
from django.conf import settings

# Check if we're running migrations
RUNNING_MIGRATIONS = 'makemigrations' in sys.argv or 'migrate' in sys.argv

class RAGProcessor:
    """Class for Retrieval-Augmented Generation on legal documents."""
    
    def __init__(self, model_name: str = None):
        """Initialize the RAG processor with the specified embedding model."""
        # Get embedding model from settings or use default
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Directory containing legal knowledge base documents
        self.knowledge_base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                              'data', 'legal_knowledge')
        
        # Only initialize embeddings if not running migrations
        if not RUNNING_MIGRATIONS:
            try:
                self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
            except Exception as e:
                print(f"Error initializing embeddings: {e}")
                print("RAG functionality will be limited.")
        
    def load_knowledge_base(self):
        """Load the legal knowledge base into the vector store."""
        if RUNNING_MIGRATIONS:
            return None
            
        if not self.embeddings:
            print("Embeddings not initialized. Cannot load knowledge base.")
            return None
            
        documents = []
        
        # Check if knowledge base directory exists
        if not os.path.exists(self.knowledge_base_dir):
            os.makedirs(self.knowledge_base_dir, exist_ok=True)
            # In a real app, you would download or create initial knowledge base files here
            
        # Load all text files from the knowledge base directory
        for filename in os.listdir(self.knowledge_base_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.knowledge_base_dir, filename)
                try:
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        # If no documents found, create a minimal knowledge base
        if not documents:
            print("No knowledge base documents found. Creating minimal knowledge base.")
            self._create_minimal_knowledge_base()
            return self.load_knowledge_base()
        
        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)
        
        # Create vector store
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        return self.vector_store
    
    def _create_minimal_knowledge_base(self):
        """Create a minimal knowledge base with some basic legal information."""
        os.makedirs(self.knowledge_base_dir, exist_ok=True)
        
        # Create a basic legal terms file
        with open(os.path.join(self.knowledge_base_dir, 'legal_terms.txt'), 'w') as f:
            f.write("""
            # Common Legal Terms in Contracts

            ## Force Majeure
            A clause that frees both parties from obligation if an extraordinary event prevents one or both parties from performing.

            ## Indemnification
            A provision where one party agrees to compensate the other party for losses or damages.

            ## Non-Compete Clause
            A clause that restricts one party from engaging in business activities that compete with the other party.

            ## Termination Clause
            Specifies how and when the contract can be terminated by either party.

            ## Confidentiality Agreement
            A provision that restricts parties from disclosing confidential information.

            ## Arbitration Clause
            A clause that requires disputes to be resolved through arbitration rather than litigation.

            ## Limitation of Liability
            A provision that limits the amount one party can be required to pay if there is a breach of contract.
            """)
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Document]:
        """Retrieve relevant context from the knowledge base for a given query."""
        if RUNNING_MIGRATIONS:
            return []
            
        if self.vector_store is None:
            self.load_knowledge_base()
            
        if self.vector_store is None:
            return []
            
        retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
        return retriever.get_relevant_documents(query)
    
    def get_legal_context(self, clause_text: str) -> Dict[str, Any]:
        """Get legal context for a specific clause."""
        if RUNNING_MIGRATIONS:
            return {'sources': [], 'relevant_info': []}
            
        # Extract key terms or concepts from the clause
        # In a real implementation, you might use NLP techniques to extract key terms
        
        # For simplicity, we'll just use the first 100 characters as the query
        query = clause_text[:100]
        
        # Retrieve relevant context
        context_docs = self.retrieve_context(query)
        
        # Format the results
        context = {
            'sources': [],
            'relevant_info': []
        }
        
        for doc in context_docs:
            context['sources'].append(doc.metadata.get('source', 'Unknown source'))
            context['relevant_info'].append(doc.page_content)
        
        return context


# Initialize a global RAG processor instance
rag_processor = RAGProcessor()

def get_legal_context_for_clause(clause_text: str) -> Dict[str, Any]:
    """Get legal context for a clause using the RAG processor."""
    return rag_processor.get_legal_context(clause_text) 