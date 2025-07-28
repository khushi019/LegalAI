import os
import sys
from typing import Dict, Any, Optional, List
from transformers.pipelines import pipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
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
        
    def _initialize_llm(self):
        """Initialize the LLM pipeline."""
        try:
            # Initialize the text generation pipeline
            pipe = pipeline(
                "text-generation",
                model=self.model_name,
                max_length=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
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
        
        # Create prompt template for explanation
        template = """
        You are a helpful legal assistant that explains complex legal language in simple terms.
        
        LEGAL CLAUSE:
        {clause}
        
        {context_prompt}
        
        Your task is to:
        1. Explain the above clause in plain, simple English that a non-lawyer can understand.
        2. Be concise but thorough.
        3. Avoid legal jargon unless you explain what it means.
        4. Focus on the practical implications for the reader.
        
        PLAIN ENGLISH EXPLANATION:
        """
        
        # Add context if available
        context_prompt = ""
        if legal_context and legal_context.get('relevant_info'):
            context_prompt = "RELEVANT LEGAL CONTEXT:\n"
            for info in legal_context.get('relevant_info', []):
                context_prompt += f"- {info}\n"
        
        prompt = PromptTemplate(
            input_variables=["clause", "context_prompt"],
            template=template
        )
        
        # Create and run the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(clause=clause_text, context_prompt=context_prompt)
        
        return result.strip()
    
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
        
        # Create a summary of the clauses
        clause_summaries = []
        for i, clause in enumerate(clauses[:5]):  # Limit to first 5 clauses for summary
            clause_summaries.append(f"{i+1}. {clause['text'][:100]}...")
        
        clause_text = "\n".join(clause_summaries)
        
        # Create prompt template for document summary
        template = """
        You are a helpful legal assistant that summarizes legal documents.
        
        DOCUMENT CLAUSES (sample):
        {clauses}
        
        Your task is to:
        1. Provide a brief overview of what this document appears to be.
        2. Identify the general purpose and type of the document.
        3. Be concise but informative.
        
        DOCUMENT SUMMARY:
        """
        
        prompt = PromptTemplate(
            input_variables=["clauses"],
            template=template
        )
        
        # Create and run the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(clauses=clause_text)
        
        return result.strip()


# Initialize a global LLM processor instance
llm_processor = LLMProcessor()

def explain_legal_clause(clause_text: str, legal_context: Optional[Dict[str, Any]] = None) -> str:
    """Generate a plain English explanation of a legal clause."""
    return llm_processor.explain_clause(clause_text, legal_context)

def summarize_legal_document(clauses: List[Dict[str, Any]]) -> str:
    """Generate an overall summary of the document based on its clauses."""
    return llm_processor.summarize_document(clauses)



    
     