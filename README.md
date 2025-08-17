# LegalDoc AI - Intelligent Contract Analyzer and Risk Detector

An AI-powered application that enables users to upload legal documents and receive clause-by-clause explanations in plain English along with risk analysis of potentially unfair or harmful clauses.

## Features

- PDF parsing and intelligent clause chunking
- Clause-level explanation in simplified, plain English using LLMs
- Retrieval-Augmented Generation (RAG) pipeline for clause-specific contextualization
- Machine Learning classifier to detect and highlight risky or unfair clauses
- Legal clause summarization and keyword highlighting
- User-friendly interface for document upload and analysis
- Export of AI-reviewed documents or risk summary report

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML/CSS/JavaScript, Bootstrap
- **AI & NLP**: 
  - LLM: facebook/opt-125m
  - Embeddings: sentence-transformers/all-MiniLM-L6-v2
  - LangChain with RAG Pipeline
- **Vector Store**: FAISS
- **PDF Parsing**: PyMuPDF, pdfplumber
- **ML & Data Science**: scikit-learn, PyTorch, Transformers
- **Database**: MySql

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/legaldoc-ai.git
   cd legaldoc-ai
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   Key dependencies include:
   - Django 4.2.7
   - LangChain 0.0.335 and LangChain Community 0.2.10
   - FAISS CPU 1.7.4
   - PyMuPDF 1.23.6 and pdfplumber 0.10.2
   - Transformers 4.35.2
   - PyTorch 2.1.1
   - sentence-transformers 2.2.2

4. Create a `.env` file in the project root with the following content:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   LLM_MODEL=facebook/opt-125m
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

5. Run the setup script to create database tables and a superuser
 
### Running the Application

1. Start the development server:
   ```
   python manage.py runserver
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

3. Log in with the superuser credentials you created during setup.

4. Upload a legal document (PDF) for analysis.

## Usage Guide

1. **Upload Document**: Click the "Upload Document" button on the home page and fill out the form.

2. **View Document**: After uploading, you'll be redirected to the document detail page where you can see the extracted clauses.

3. **Analyze Clauses**: The system will automatically analyze each clause. If analysis is not complete, click the "Analyze Now" button.

4. **View Report**: Click the "View Report" button to see an overall analysis of the document, including risk assessment and highlighted risky clauses.

## Development

### Project Structure

- `legaldoc_ai/` - Django project directory
- `document_analyzer/` - Main application for document processing
- `legal_classifier/` - ML model for risk classification
- `rag_pipeline/` - Retrieval-Augmented Generation components
- `templates/` - HTML templates
- `static/` - CSS, JS, and other static files
- `data/legal_knowledge/` - Knowledge base for RAG pipeline

### Running Tests

```
python manage.py test
```

## Acknowledgments

- Hugging Face for providing open-source models
- LangChain for the RAG pipeline framework
- Django community for the web framework 
