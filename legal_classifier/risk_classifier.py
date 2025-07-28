import os
import json
import sys
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from transformers.pipelines import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Check if we're running migrations
RUNNING_MIGRATIONS = 'makemigrations' in sys.argv or 'migrate' in sys.argv

class RiskClassifier:
    """Class for classifying legal clauses based on risk level."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the risk classifier."""
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.risk_keywords = {
            'high': [
                'waive', 'waiver', 'indemnify', 'indemnification', 'liability', 
                'unlimited liability', 'termination without notice', 'unilateral', 
                'non-negotiable', 'forfeit', 'penalty', 'mandatory arbitration',
                'class action waiver', 'non-refundable'
            ],
            'medium': [
                'terminate', 'termination', 'confidential', 'confidentiality',
                'non-compete', 'non-solicitation', 'intellectual property',
                'assignment', 'governing law', 'jurisdiction', 'arbitration'
            ],
            'low': [
                'notice', 'payment', 'term', 'renewal', 'amendment', 'modification',
                'communication', 'severability', 'entire agreement'
            ]
        }
        
        # Initialize fallback classifier
        self.fallback_classifier = self._create_fallback_classifier()
        
        # Try to load the transformer model if available and not running migrations
        if not RUNNING_MIGRATIONS:
            self._load_model()
    
    def _load_model(self):
        """Load the transformer model for clause classification."""
        try:
            if self.model_path and os.path.exists(self.model_path):
                # Import these only when needed to avoid issues during migrations
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
                print(f"Loaded transformer model from {self.model_path}")
            else:
                # In a real application, you might download a pre-trained model
                # or use a hosted API for inference
                print("No transformer model found, using fallback classifier")
        except Exception as e:
            print(f"Error loading transformer model: {e}")
            print("Using fallback classifier")
    
    def _create_fallback_classifier(self):
        """Create a simple fallback classifier using TF-IDF and Naive Bayes."""
        # This is a very simple classifier for demonstration purposes
        # In a real application, you would use a more sophisticated model
        
        # Sample training data
        X = [
            # High risk clauses
            "The user waives all rights to pursue legal action against the company.",
            "You agree to indemnify and hold harmless the company from any claims.",
            "The company reserves the right to terminate service without notice.",
            "You forfeit all payments made if you cancel the service.",
            "You waive your right to participate in a class action lawsuit.",
            
            # Medium risk clauses
            "Either party may terminate this agreement with 30 days notice.",
            "You agree to keep all information confidential for a period of 5 years.",
            "This agreement is governed by the laws of the state of California.",
            "Any disputes shall be resolved through binding arbitration.",
            "You agree not to compete with the company for 1 year after termination.",
            
            # Low risk clauses
            "Payments are due on the first of each month.",
            "The term of this agreement is 12 months.",
            "Notices must be sent in writing to the address provided.",
            "This agreement constitutes the entire understanding between the parties.",
            "If any provision is found invalid, the remainder shall remain in effect."
        ]
        
        y = ['high', 'high', 'high', 'high', 'high',
             'medium', 'medium', 'medium', 'medium', 'medium',
             'low', 'low', 'low', 'low', 'low']
        
        # Create and train the pipeline
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000)),
            ('clf', MultinomialNB())
        ])
        
        pipeline.fit(X, y)
        return pipeline
    
    def _extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract risk keywords from the text."""
        text_lower = text.lower()
        found_keywords = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for risk_level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_keywords[risk_level].append(keyword)
        
        return found_keywords
    
    def _classify_with_transformer(self, text: str) -> Tuple[str, float]:
        """Classify text using the transformer model."""
        # Import torch only when needed to avoid issues during migrations
        import torch
        
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Assuming labels are ordered as ['low', 'medium', 'high']
            predicted_class_idx = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class_idx].item()
            
            risk_levels = ['low', 'medium', 'high']
            predicted_risk = risk_levels[predicted_class_idx]
            
            return predicted_risk, confidence
    
    def _classify_with_fallback(self, text: str) -> Tuple[str, float]:
        """Classify text using the fallback classifier."""
        # Get probability estimates
        probas = self.fallback_classifier.predict_proba([text])[0]
        
        # Get the predicted class and its probability
        predicted_class_idx = np.argmax(probas)
        confidence = probas[predicted_class_idx]
        
        # Map index to class label
        classes = self.fallback_classifier.classes_
        predicted_risk = classes[predicted_class_idx]
        
        return predicted_risk, confidence
    
    def classify(self, clause_text: str) -> Dict[str, Any]:
        """Classify a legal clause based on risk level."""
        if RUNNING_MIGRATIONS:
            return {
                'risk_level': 'low',
                'confidence': 1.0,
                'keywords': [],
                'explanation': "This is a placeholder during migrations."
            }
            
        # Extract keywords
        keywords = self._extract_keywords(clause_text)
        
        # Determine risk level based on keywords
        keyword_risk = 'low'
        if keywords['high']:
            keyword_risk = 'high'
        elif keywords['medium']:
            keyword_risk = 'medium'
        
        # Use transformer model if available, otherwise use fallback
        if self.model and self.tokenizer:
            model_risk, confidence = self._classify_with_transformer(clause_text)
        else:
            model_risk, confidence = self._classify_with_fallback(clause_text)
        
        # Combine keyword-based and model-based classifications
        # If high-risk keywords are found, increase the risk level
        final_risk = model_risk
        if keyword_risk == 'high' and model_risk != 'high':
            final_risk = 'high'
        elif keyword_risk == 'medium' and model_risk == 'low':
            final_risk = 'medium'
        
        # Prepare explanation based on risk level
        explanation = self._generate_explanation(final_risk, keywords)
        
        # Flatten the keywords for easier storage
        flat_keywords = []
        for risk_level, words in keywords.items():
            flat_keywords.extend(words)
        
        return {
            'risk_level': final_risk,
            'confidence': confidence,
            'keywords': flat_keywords,
            'explanation': explanation
        }
    
    def _generate_explanation(self, risk_level: str, keywords: Dict[str, List[str]]) -> str:
        """Generate an explanation for the risk classification."""
        if risk_level == 'high':
            explanation = "This clause contains high-risk elements that may be unfavorable."
            if keywords['high']:
                explanation += f" High-risk terms found: {', '.join(keywords['high'])}."
        elif risk_level == 'medium':
            explanation = "This clause contains medium-risk elements that warrant attention."
            if keywords['medium']:
                explanation += f" Medium-risk terms found: {', '.join(keywords['medium'])}."
        else:
            explanation = "This clause appears to be standard with low risk."
            if keywords['low']:
                explanation += f" Common legal terms found: {', '.join(keywords['low'])}."
        
        return explanation


# Initialize a global risk classifier instance
risk_classifier = RiskClassifier()

def classify_clause_risk(clause_text: str) -> Dict[str, Any]:
    """Classify a clause's risk level using the risk classifier."""
    return risk_classifier.classify(clause_text) 