import re
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any, Tuple

class PDFProcessor:
    """Class for processing PDF documents and extracting clauses."""
    
    def __init__(self, file_path: str):
        """Initialize with the path to the PDF file."""
        self.file_path = file_path
        
    def extract_text(self) -> str:
        """Extract all text from the PDF document."""
        text = ""
        try:
            # Using PyMuPDF (faster but sometimes less accurate)
            doc = fitz.open(self.file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error with PyMuPDF: {e}")
            # Fallback to pdfplumber (slower but more accurate)
            try:
                with pdfplumber.open(self.file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            except Exception as e2:
                print(f"Error with pdfplumber: {e2}")
                raise Exception(f"Failed to extract text from PDF: {e2}")
        
        return text
    
    def extract_clauses(self) -> List[Dict[str, Any]]:
        """Extract clauses from the PDF document."""
        text = self.extract_text()
        clauses = []
        
        # Extract clauses based on patterns (this is a simplified approach)
        # In a real implementation, you might use more sophisticated NLP techniques
        
        # Simple pattern: numbered sections, paragraphs, or clauses
        patterns = [
            r'(\d+\.\s+[A-Z][^.]+\.)',  # Numbered sections: "1. TERM."
            r'(Section\s+\d+\.\s+[^.]+\.)',  # Section headers: "Section 1. Term."
            r'(\([a-z]\)\s+[^.]+\.)',  # Lettered clauses: "(a) This is a clause."
            r'(ARTICLE\s+[IVX]+\.\s+[^.]+\.)'  # Article headers: "ARTICLE I. DEFINITIONS."
        ]
        
        page_num = 1  # Default to page 1 if we can't determine actual page
        position = 0
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                clause_text = match.group(0)
                # Try to get more context by including the next paragraph
                next_text = text[match.end():match.end() + 500]
                if next_text:
                    clause_text += " " + next_text
                
                clauses.append({
                    'text': clause_text.strip(),
                    'page_number': page_num,
                    'position': position
                })
                position += 1
        
        # If no clauses found with patterns, fall back to paragraph splitting
        if not clauses:
            paragraphs = re.split(r'\n\s*\n', text)
            for i, para in enumerate(paragraphs):
                if len(para.strip()) > 50:  # Only include substantial paragraphs
                    clauses.append({
                        'text': para.strip(),
                        'page_number': page_num,
                        'position': i
                    })
        
        return clauses
    
    def get_document_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the PDF document."""
        metadata = {}
        try:
            doc = fitz.open(self.file_path)
            metadata = doc.metadata
            doc.close()
        except Exception:
            pass
        
        return metadata


def process_document(document_instance) -> List[Dict[str, Any]]:
    """Process a document and extract clauses."""
    processor = PDFProcessor(document_instance.file.path)
    clauses = processor.extract_clauses()
    return clauses 