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
		# Enhanced fallback that provides actual English translations
		clause_lower = clause_text.lower()
		clause_text_clean = clause_text.strip()
		
		# Extract key information and translate to simple English
		explanations = []
		
		# Termination clauses
		if "terminat" in clause_lower:
			if "without notice" in clause_lower or "immediate" in clause_lower:
				explanations.append("This clause allows either party to end the agreement immediately without giving advance notice.")
			elif "with notice" in clause_lower or "days" in clause_lower or "weeks" in clause_lower:
				notice_period = self._extract_number(clause_text, ["day", "week", "month"])
				if notice_period:
					explanations.append(f"This clause allows either party to end the agreement by giving {notice_period} advance notice.")
				else:
					explanations.append("This clause describes how and when the agreement can be ended by either party with advance notice.")
			else:
				explanations.append("This clause explains the conditions and process for ending this agreement.")
		
		# Confidentiality clauses
		if "confidential" in clause_lower or "non-disclosure" in clause_lower:
			duration = self._extract_number(clause_text, ["year", "month"])
			if duration:
				explanations.append(f"This clause requires both parties to keep sensitive information private and not share it with others for {duration}.")
			else:
				explanations.append("This clause requires both parties to keep sensitive information private and not share it with others.")
		
		# Indemnification clauses
		if "indemni" in clause_lower:
			explanations.append("This clause means that one party agrees to pay for any losses or damages that the other party might face because of this agreement.")
		
		# Payment and fee clauses
		if "payment" in clause_lower or "fee" in clause_lower or "compensation" in clause_lower:
			amount = self._extract_amount(clause_text)
			payment_terms = []
			if "monthly" in clause_lower or "per month" in clause_lower:
				payment_terms.append("monthly")
			if "annual" in clause_lower or "per year" in clause_lower:
				payment_terms.append("annually")
			if "due" in clause_lower:
				payment_terms.append("when payment is due")
			if amount:
				terms_str = " and ".join(payment_terms) if payment_terms else ""
				explanations.append(f"This clause specifies payment terms: {amount} {terms_str}.")
			else:
				explanations.append("This clause explains the payment terms, amounts, and when payments are due.")
		
		# Arbitration and dispute resolution
		if "arbitration" in clause_lower:
			explanations.append("This clause means that if there are any disagreements, they will be resolved through arbitration (a private process) instead of going to court.")
		elif "disput" in clause_lower or "disagreement" in clause_lower:
			explanations.append("This clause explains how any disagreements or disputes between the parties will be resolved.")
		
		# Liability and waiver clauses
		if "liability" in clause_lower or "liable" in clause_lower:
			if "limit" in clause_lower or "maximum" in clause_lower:
				explanations.append("This clause limits how much one party can be held responsible for damages or losses.")
			else:
				explanations.append("This clause explains the responsibilities and liabilities of each party.")
		
		if "waive" in clause_lower or "waiver" in clause_lower:
			explanations.append("This clause means that one or both parties are giving up certain rights or claims.")
		
		# Non-compete clauses
		if "non-compete" in clause_lower or "non compete" in clause_lower:
			duration = self._extract_number(clause_text, ["year", "month"])
			if duration:
				explanations.append(f"This clause prevents one party from working with or starting a competing business for {duration} after the agreement ends.")
			else:
				explanations.append("This clause restricts one party from competing with the other party's business.")
		
		# Intellectual property clauses
		if "intellectual property" in clause_lower or "copyright" in clause_lower or "patent" in clause_lower:
			explanations.append("This clause explains who owns the rights to ideas, inventions, or creative work created during this agreement.")
		
		# Governing law clauses
		if "governing law" in clause_lower or "laws of" in clause_lower or "jurisdiction" in clause_lower:
			location = self._extract_location(clause_text)
			if location:
				explanations.append(f"This clause states that the laws of {location} will apply to this agreement.")
			else:
				explanations.append("This clause specifies which state or country's laws will govern this agreement.")
		
		# Amendment and modification clauses
		if "amend" in clause_lower or "modif" in clause_lower or "change" in clause_lower:
			explanations.append("This clause explains how this agreement can be changed or updated in the future.")
		
		# Force majeure clauses
		if "force majeure" in clause_lower or "act of god" in clause_lower:
			explanations.append("This clause explains what happens if events outside of either party's control (like natural disasters) prevent them from fulfilling their obligations.")
		
		# Severability clauses
		if "severability" in clause_lower or "severable" in clause_lower:
			explanations.append("This clause means that if one part of the agreement is found to be invalid, the rest of the agreement will still be valid.")
		
		# Entire agreement clauses
		if "entire agreement" in clause_lower or "complete agreement" in clause_lower:
			explanations.append("This clause states that this document contains the complete agreement between the parties and replaces any previous agreements.")
		
		# If no specific clause type identified, try to extract the main purpose
		if not explanations:
			# Try to understand the clause by looking for common patterns
			if len(clause_text_clean) < 200:
				# For short clauses, try to explain in simple terms
				explanations.append(f"This clause states: {self._simplify_language(clause_text_clean[:150])}")
			else:
				# For longer clauses, summarize the key points
				key_points = self._extract_key_points(clause_text_clean)
				if key_points:
					explanations.extend(key_points)
		else:
					explanations.append("This clause contains important terms and conditions that both parties must follow.")
		
		return " ".join(explanations)
	
	def _extract_number(self, text: str, units: List[str]) -> str:
		"""Extract a number with unit from text."""
		import re
		for unit in units:
			pattern = r'(\d+)\s*' + unit
			match = re.search(pattern, text, re.IGNORECASE)
			if match:
				number = match.group(1)
				return f"{number} {unit}{'s' if int(number) != 1 else ''}"
		return ""
	
	def _extract_amount(self, text: str) -> str:
		"""Extract monetary amount from text."""
		import re
		# Look for currency amounts
		patterns = [
			r'\$[\d,]+\.?\d*',  # $1,000 or $1000.50
			r'[\d,]+\.?\d*\s*(dollars|USD|rupees|INR)',  # 1000 dollars
		]
		for pattern in patterns:
			match = re.search(pattern, text, re.IGNORECASE)
			if match:
				return match.group(0)
		return ""
	
	def _extract_location(self, text: str) -> str:
		"""Extract location from governing law clause."""
		import re
		# Look for "laws of [location]" or "governed by [location]"
		patterns = [
			r'laws of ([A-Z][a-zA-Z\s]+?)(?:\.|,|$)',
			r'governed by.*?([A-Z][a-zA-Z\s]+?)(?:\.|,|$)',
		]
		for pattern in patterns:
			match = re.search(pattern, text)
			if match:
				location = match.group(1).strip()
				# Limit to reasonable length
				if len(location) < 50:
					return location
		return ""
	
	def _simplify_language(self, text: str) -> str:
		"""Simplify legal language to plain English."""
		# Replace common legal terms with simpler equivalents
		replacements = {
			'shall': 'must',
			'may': 'can',
			'herein': 'in this document',
			'thereof': 'of it',
			'thereto': 'to it',
			'therein': 'in it',
			'pursuant to': 'according to',
			'notwithstanding': 'despite',
			'whereas': 'given that',
			'party of the first part': 'first party',
			'party of the second part': 'second party',
		}
		result = text
		for legal_term, simple_term in replacements.items():
			result = result.replace(legal_term, simple_term)
			result = result.replace(legal_term.capitalize(), simple_term.capitalize())
		return result
	
	def _extract_key_points(self, text: str) -> List[str]:
		"""Extract key points from a longer clause."""
		# Simple sentence-based extraction
		import re
		sentences = re.split(r'[.!?]+', text)
		key_points = []
		for sentence in sentences[:3]:  # Take first 3 sentences
			sentence = sentence.strip()
			if len(sentence) > 20 and len(sentence) < 200:
				simplified = self._simplify_language(sentence)
				key_points.append(simplified)
		return key_points
	
	def summarize_document(self, clauses: List[Dict[str, Any]]) -> str:
		"""Generate a comprehensive point-wise executive summary of the document."""
		if not clauses:
			return "This document contains multiple legal clauses. Please review each section carefully."
		
		# Analyze all clauses to build a comprehensive summary
		summary_points = []
		
		# Categorize clauses by type
		clause_categories = {
			'termination': [],
			'payment': [],
			'confidentiality': [],
			'indemnification': [],
			'liability': [],
			'dispute_resolution': [],
			'non_compete': [],
			'intellectual_property': [],
			'governing_law': [],
			'amendment': [],
			'force_majeure': [],
			'other': []
		}
		
		# Analyze each clause - a clause can belong to multiple categories
		for clause in clauses:
			text = clause.get('text', '')
			text_lower = text.lower()
			
			# Categorize the clause - check all categories as clauses can have multiple aspects
			categorized = False
			
			# High priority categories (more specific)
			if 'terminat' in text_lower:
				clause_categories['termination'].append(text)
				categorized = True
			if 'payment' in text_lower or 'fee' in text_lower or 'compensation' in text_lower or 'salary' in text_lower or 'wage' in text_lower:
				clause_categories['payment'].append(text)
				categorized = True
			if 'confidential' in text_lower or 'non-disclosure' in text_lower or 'nda' in text_lower:
				clause_categories['confidentiality'].append(text)
				categorized = True
			if 'indemni' in text_lower:
				clause_categories['indemnification'].append(text)
				categorized = True
			if 'liability' in text_lower or 'liable' in text_lower:
				clause_categories['liability'].append(text)
				categorized = True
			if 'arbitration' in text_lower or 'disput' in text_lower or 'litigation' in text_lower:
				clause_categories['dispute_resolution'].append(text)
				categorized = True
			if 'non-compete' in text_lower or 'non compete' in text_lower:
				clause_categories['non_compete'].append(text)
				categorized = True
			if 'intellectual property' in text_lower or 'copyright' in text_lower or 'patent' in text_lower or 'trademark' in text_lower:
				clause_categories['intellectual_property'].append(text)
				categorized = True
			if 'governing law' in text_lower or 'laws of' in text_lower or 'jurisdiction' in text_lower:
				clause_categories['governing_law'].append(text)
				categorized = True
			if 'amend' in text_lower or 'modif' in text_lower:
				clause_categories['amendment'].append(text)
				categorized = True
			if 'force majeure' in text_lower or 'act of god' in text_lower:
				clause_categories['force_majeure'].append(text)
				categorized = True
			
			# If no specific category matched, add to other
			if not categorized:
				clause_categories['other'].append(text)
		
		# Build summary points for each category
		
		# Document Overview
		total_clauses = len(clauses)
		summary_points.append(f"**Document Overview:** This document is a legal agreement containing {total_clauses} clause{'s' if total_clauses != 1 else ''}.")
		
		# Termination Clauses
		if clause_categories['termination']:
			termination_details = []
			for term_clause in clause_categories['termination']:
				term_lower = term_clause.lower()
				if 'without notice' in term_lower or 'immediate' in term_lower:
					termination_details.append("immediate termination without notice")
				elif 'with notice' in term_lower:
					notice_period = self._extract_number(term_clause, ["day", "week", "month"])
					if notice_period:
						termination_details.append(f"termination with {notice_period} notice")
					else:
						termination_details.append("termination with advance notice")
			if termination_details:
				unique_details = list(set(termination_details))
				summary_points.append(f"**Termination:** The agreement can be ended {', or '.join(unique_details)}.")
			else:
				summary_points.append("**Termination:** The document includes terms for how and when the agreement can be terminated.")
		
		# Payment Clauses
		if clause_categories['payment']:
			payment_details = []
			for pay_clause in clause_categories['payment']:
				amount = self._extract_amount(pay_clause)
				pay_lower = pay_clause.lower()
				if amount:
					payment_details.append(amount)
				if 'monthly' in pay_lower:
					payment_details.append("monthly payments")
				if 'annual' in pay_lower or 'yearly' in pay_lower:
					payment_details.append("annual payments")
			if payment_details:
				unique_payments = list(set(payment_details))[:3]  # Limit to 3 most important
				summary_points.append(f"**Payment Terms:** The agreement specifies {', '.join(unique_payments)}.")
			else:
				summary_points.append("**Payment Terms:** The document includes detailed payment terms, amounts, and schedules.")
		
		# Confidentiality Clauses
		if clause_categories['confidentiality']:
			conf_details = []
			for conf_clause in clause_categories['confidentiality']:
				duration = self._extract_number(conf_clause, ["year", "month"])
				if duration:
					conf_details.append(f"confidentiality obligations for {duration}")
			if conf_details:
				summary_points.append(f"**Confidentiality:** Both parties must keep sensitive information private. {', '.join(conf_details)}.")
			else:
				summary_points.append("**Confidentiality:** The document requires both parties to maintain confidentiality of sensitive information.")
		
		# Indemnification Clauses
		if clause_categories['indemnification']:
			summary_points.append("**Indemnification:** One party agrees to compensate the other party for losses or damages arising from this agreement.")
		
		# Liability Clauses
		if clause_categories['liability']:
			liability_details = []
			for liab_clause in clause_categories['liability']:
				liab_lower = liab_clause.lower()
				if 'limit' in liab_lower or 'maximum' in liab_lower:
					liability_details.append("limited liability")
				if 'waive' in liab_lower:
					liability_details.append("liability waivers")
			if liability_details:
				summary_points.append(f"**Liability:** The document includes {', '.join(set(liability_details))} provisions.")
			else:
				summary_points.append("**Liability:** The document specifies the responsibilities and liabilities of each party.")
		
		# Dispute Resolution Clauses
		if clause_categories['dispute_resolution']:
			for disp_clause in clause_categories['dispute_resolution']:
				disp_lower = disp_clause.lower()
				if 'arbitration' in disp_lower:
					summary_points.append("**Dispute Resolution:** Disagreements will be resolved through arbitration instead of court proceedings.")
					break
				elif 'litigation' in disp_lower or 'court' in disp_lower:
					summary_points.append("**Dispute Resolution:** Disagreements will be resolved through court proceedings.")
					break
			else:
				summary_points.append("**Dispute Resolution:** The document specifies how disputes will be resolved between the parties.")
		
		# Non-Compete Clauses
		if clause_categories['non_compete']:
			nc_details = []
			for nc_clause in clause_categories['non_compete']:
				duration = self._extract_number(nc_clause, ["year", "month"])
				if duration:
					nc_details.append(f"{duration} restriction")
			if nc_details:
				summary_points.append(f"**Non-Compete:** The agreement restricts one party from competing for {', '.join(nc_details)} after termination.")
			else:
				summary_points.append("**Non-Compete:** The document includes restrictions on competitive activities.")
		
		# Intellectual Property Clauses
		if clause_categories['intellectual_property']:
			summary_points.append("**Intellectual Property:** The document specifies ownership rights for ideas, inventions, or creative work.")
		
		# Governing Law Clauses
		if clause_categories['governing_law']:
			for gov_clause in clause_categories['governing_law']:
				location = self._extract_location(gov_clause)
				if location:
					summary_points.append(f"**Governing Law:** The laws of {location} will govern this agreement.")
					break
		else:
				summary_points.append("**Governing Law:** The document specifies which jurisdiction's laws apply to this agreement.")
		
		# Amendment Clauses
		if clause_categories['amendment']:
			summary_points.append("**Amendments:** The document explains how the agreement can be modified or updated in the future.")
		
		# Force Majeure Clauses
		if clause_categories['force_majeure']:
			summary_points.append("**Force Majeure:** The document includes provisions for circumstances beyond either party's control (such as natural disasters).")
		
		# Other Important Clauses
		if clause_categories['other']:
			# Try to identify other important clauses
			other_important = []
			for other_clause in clause_categories['other'][:5]:  # Check first 5 other clauses
				other_lower = other_clause.lower()
				if 'severability' in other_lower:
					other_important.append("severability")
				if 'entire agreement' in other_lower:
					other_important.append("entire agreement")
				if 'notice' in other_lower and 'termination' not in other_lower:
					other_important.append("notice requirements")
				if 'assignment' in other_lower:
					other_important.append("assignment rights")
			if other_important:
				summary_points.append(f"**Additional Terms:** The document also includes {', '.join(set(other_important))} provisions.")
		
		# Risk Summary
		if len(clause_categories['indemnification']) > 0 or len(clause_categories['liability']) > 0:
			summary_points.append("**Risk Considerations:** This document contains indemnification and liability clauses that may have significant financial implications.")
		
		# Join all points with double newlines for proper paragraph separation
		return "\n\n".join(summary_points)


# Initialize a global LLM processor instance
llm_processor = LLMProcessor()

def explain_legal_clause(clause_text: str, legal_context: Optional[Dict[str, Any]] = None) -> str:
	"""Generate a plain English explanation of a legal clause."""
	return llm_processor.explain_clause(clause_text, legal_context)

def summarize_legal_document(clauses: List[Dict[str, Any]]) -> str:
	"""Generate an overall summary of the document based on its clauses."""
	return llm_processor.summarize_document(clauses)



    
     