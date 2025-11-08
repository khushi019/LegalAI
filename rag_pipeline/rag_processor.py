import os
import sys
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from django.conf import settings
import pdfplumber

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
			chunk_size=1200,
			chunk_overlap=200
		)
		
		# Directories containing legal knowledge base documents
		base_dir = os.path.dirname(os.path.dirname(__file__))
		self.knowledge_base_dirs = [
			os.path.join(base_dir, 'data', 'legal_knowledge'),
			os.path.join(base_dir, 'data', 'legal_cases'),
		]
		
		# Only initialize embeddings if not running migrations
		if not RUNNING_MIGRATIONS:
			try:
				self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
			except Exception as e:
				print(f"Error initializing embeddings: {e}")
				print("RAG functionality will be limited.")
		
	def _ensure_dirs(self):
		for d in self.knowledge_base_dirs:
			os.makedirs(d, exist_ok=True)
	
	def _load_txt_md(self, file_path: str) -> List[Document]:
		loader = TextLoader(file_path)
		return loader.load()
	
	def _load_pdf(self, file_path: str) -> List[Document]:
		texts: List[Document] = []
		try:
			with pdfplumber.open(file_path) as pdf:
				content_parts: List[str] = []
				for page in pdf.pages:
					content_parts.append(page.extract_text() or '')
				full_text = "\n\n".join(content_parts).strip()
				if full_text:
					texts.append(Document(page_content=full_text, metadata={"source": file_path}))
		except Exception as e:
			print(f"Error loading PDF {file_path}: {e}")
		return texts
	
	def _create_minimal_knowledge_base(self):
		"""Create a minimal knowledge base with some basic legal information."""
		self._ensure_dirs()
		# Seed a couple of basic files if empty
		seed_dir = self.knowledge_base_dirs[0]
		legal_terms_path = os.path.join(seed_dir, 'legal_terms.txt')
		if not os.path.exists(legal_terms_path):
			with open(legal_terms_path, 'w', encoding='utf-8') as f:
				f.write(
"""
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
"""
				)
	
	def load_knowledge_base(self, extra_dirs: List[str] | None = None):
		"""Load the legal knowledge base into the vector store.
		Optionally include additional directories (absolute or relative) containing .txt, .md, .pdf files.
		"""
		if RUNNING_MIGRATIONS:
			return None
		if not self.embeddings:
			print("Embeddings not initialized. Cannot load knowledge base.")
			return None
		
		self._ensure_dirs()
		documents: List[Document] = []
		search_dirs = list(self.knowledge_base_dirs)
		if extra_dirs:
			for d in extra_dirs:
				search_dirs.append(os.path.abspath(d))
		
		for directory in search_dirs:
			if not os.path.exists(directory):
				continue
			for root, _, files in os.walk(directory):
				for name in files:
					file_path = os.path.join(root, name)
					lower = name.lower()
					if lower.endswith('.txt') or lower.endswith('.md'):
						documents.extend(self._load_txt_md(file_path))
					elif lower.endswith('.pdf'):
						documents.extend(self._load_pdf(file_path))
		
		# If no documents found, create a minimal knowledge base and try again
		if not documents:
			print("No knowledge base documents found. Creating minimal knowledge base.")
			self._create_minimal_knowledge_base()
			return self.load_knowledge_base(extra_dirs)
		
		# Split documents into chunks and build vector store
		texts = self.text_splitter.split_documents(documents)
		self.vector_store = FAISS.from_documents(texts, self.embeddings)
		return self.vector_store
	
	def retrieve_context(self, query: str, top_k: int = 5) -> List[Document]:
		"""Retrieve relevant context from the knowledge base for a given query."""
		if RUNNING_MIGRATIONS:
			return []
		if self.vector_store is None:
			self.load_knowledge_base()
		if self.vector_store is None:
			return []
		retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
		return retriever.invoke(query)
	
	def get_legal_context(self, clause_text: str) -> Dict[str, Any]:
		"""Get legal context for a specific clause."""
		if RUNNING_MIGRATIONS:
			return {'sources': [], 'relevant_info': []}
		query = clause_text[:200]
		context_docs = self.retrieve_context(query)
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