import os
import sys
from typing import Dict, Any, Optional, List
from transformers.pipelines import pipeline
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from django.conf import settings

# Check if we're running migrations
RUNNING_MIGRATIONS = 'makemigrations' in sys.argv or 'migrate' in sys.argv

class LLMProcessor:
	"""Class for processing legal text using LLMs."""
	
	def __init__(self, model_name: Optional[str] = None):
		"""Initialize the LLM processor with the specified model."""
		# Use the model from settings by default
		self.model_name = model_name or settings.LLM_MODEL
		self.llm = None
		
		# Only initialize LLM if not running migrations
		if not RUNNING_MIGRATIONS:
			self._initialize_llm()
		
	def _infer_task(self) -> str:
		name = (self.model_name or '').lower()
		# T5/FLAN and similar seq2seq models need text2text-generation
		if 't5' in name or 'flan' in name:
			return 'text2text-generation'
		return 'text-generation'
		
	def _initialize_llm(self):
		"""Initialize the LLM pipeline."""
		try:
			# Initialize the text generation pipeline
			task = self._infer_task()
			pipe = pipeline(
				task,
				model=self.model_name,
				max_length=256,
				temperature=0.7,
				top_p=0.95,
				repetition_penalty=1.15,
				do_sample=True,
				truncation=True
			)
			
			# Create a LangChain wrapper around the pipeline
			self.llm = HuggingFacePipeline(pipeline=pipe)
			print(f"Initialized LLM with model: {self.model_name}")
		except Exception as e:
			print(f"Error initializing LLM: {e}")
			print("LLM functionality will be limited.")
	
	def explain_clause(self, clause_text: str, legal_context: Optional[Dict[str, Any]] = None) -> str:
		"""Generate a plain English explanation of a legal clause."""
		if RUNNING_MIGRATIONS or not self.llm:
			return self._fallback_explanation(clause_text)
		
		# For now, use fallback explanation as the LLM models are not working well
		# TODO: Implement better LLM integration with a more suitable model
		return self._fallback_explanation(clause_text)
	
	def _fallback_explanation(self, clause_text: str) -> str:
		"""Generate a fallback explanation when LLM is not available."""
		# This is a very basic fallback that just identifies the type of clause
		clause_lower = clause_text.lower()
		
		if "terminat" in clause_lower:
			return "This appears to be a termination clause that describes how and when the agreement can be ended."
		elif "confidential" in clause_lower:
			return "This appears to be a confidentiality clause that requires keeping certain information private."
		elif "indemni" in clause_lower:
			return "This appears to be an indemnification clause where one party agrees to cover costs or damages incurred by the other party."
		elif "arbitration" in clause_lower or "disput" in clause_lower:
			return "This appears to be a dispute resolution clause that describes how disagreements will be handled."
		elif "payment" in clause_lower or "fee" in clause_lower:
			return "This appears to be a payment clause that describes financial obligations."
		else:
			return "This clause contains legal language. For a precise understanding, consider consulting with a legal professional."
	
	def summarize_document(self, clauses: List[Dict[str, Any]]) -> str:
		"""Generate an overall summary of the document based on its clauses."""
		if RUNNING_MIGRATIONS or not self.llm or not clauses:
			return "This document contains multiple legal clauses. Please review each section carefully."
		
		# For now, use a simple summary as the LLM models are not working well
		# TODO: Implement better LLM integration with a more suitable model
		clause_types = []
		for clause in clauses[:5]:  # Check first 5 clauses
			text = clause['text'].lower()
			if 'terminat' in text:
				clause_types.append('termination')
			elif 'payment' in text or 'fee' in text:
				clause_types.append('payment')
			elif 'confidential' in text:
				clause_types.append('confidentiality')
			elif 'indemni' in text:
				clause_types.append('indemnification')
			elif 'arbitration' in text or 'disput' in text:
				clause_types.append('dispute resolution')
		
		if clause_types:
			unique_types = list(set(clause_types))
			return f"This document appears to be a legal agreement containing clauses related to: {', '.join(unique_types)}. Please review each section carefully for specific terms and conditions."
		else:
			return "This document contains multiple legal clauses. Please review each section carefully."


# Initialize a global LLM processor instance
llm_processor = LLMProcessor()

def explain_legal_clause(clause_text: str, legal_context: Optional[Dict[str, Any]] = None) -> str:
	"""Generate a plain English explanation of a legal clause."""
	return llm_processor.explain_clause(clause_text, legal_context)

def summarize_legal_document(clauses: List[Dict[str, Any]]) -> str:
	"""Generate an overall summary of the document based on its clauses."""
	return llm_processor.summarize_document(clauses)



    
     