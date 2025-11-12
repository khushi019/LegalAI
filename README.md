# LegalDoc AI - Intelligent Contract Analyzer and Risk Detector

An AI-powered application that enables users to upload legal documents and receive clause-by-clause explanations in plain English along with risk analysis of potentially unfair or harmful clauses.

## Features

- PDF parsing and intelligent clause chunking
- **Enhanced clause explanations** in simplified, plain English with detailed translations of legal terminology
- **Comprehensive point-wise executive summaries** with categorized analysis
- Retrieval-Augmented Generation (RAG) pipeline for clause-specific contextualization
- Machine Learning classifier to detect and highlight risky or unfair clauses
- **Interactive risk assessment** with visual risk meter and detailed risk scoring
- Legal clause summarization and keyword highlighting
- User-friendly interface for document upload and analysis
- **Timezone support** (India/Kolkata - IST) for all timestamps
- Export of AI-reviewed documents or risk summary report

## Tech Stack

- **Backend**: Django 5.2.4, Django REST Framework
- **Frontend**: HTML/CSS/JavaScript, Bootstrap
- **AI & NLP**: 
   - LLM: google/flan-t5-small (configurable via environment variables)
   - Enhanced fallback explanation system for comprehensive clause translations
   - Embeddings: sentence-transformers/all-MiniLM-L6-v2
   - Retrieval-Augmented Generation (RAG) pipeline (LangChain) for context-aware clause explanations
- **Vector Store**: FAISS
- **PDF Parsing**: PyMuPDF, pdfplumber
- **ML & Data Science**: scikit-learn, PyTorch, Transformers
- **Database**: SQLite (development) - can be configured for PostgreSQL in production

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
   - Django 5.2.4
   - LangChain 0.0.335 and LangChain Community 0.2.10
   - LangChain HuggingFace integration
   - FAISS CPU 1.7.4
   - PyMuPDF 1.23.6 and pdfplumber 0.10.2
   - Transformers 4.35.2
   - PyTorch 2.1.1
   - sentence-transformers 2.2.2
   - scikit-learn 1.3.2

4. Create a `.env` file in the project root with the following content:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   LLM_MODEL=google/flan-t5-small
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

5. Run database migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser account:
   ```
   python manage.py createsuperuser
   ```

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

    - You can also check the analysis progress via the API endpoint:
       `GET /api/documents/<id>/progress/` (requires authentication). This returns total clauses, analyzed clauses, progress percentage and completion status.

4. **View Report**: Click the "View Report" button to see an overall analysis of the document, including:
   - **Executive Summary**: Comprehensive point-wise summary with categorized analysis (Termination, Payment Terms, Confidentiality, Liability, etc.)
   - **Risk Assessment**: Visual risk meter showing overall risk score (Low/Medium/High)
   - **Risk Highlights**: Detailed breakdown of high and medium risk clauses with explanations
   - All timestamps displayed in India/Kolkata timezone (IST)

## Development

### Project Structure

- `legaldoc_ai/` - Django project directory (settings, URLs, WSGI configuration)
- `document_analyzer/` - Main application for document processing
  - `llm_processor.py` - Enhanced clause explanation and document summarization
  - `document_service.py` - Document processing service layer
  - `pdf_processor.py` - PDF parsing and clause extraction
  - `models.py` - Database models (Document, Clause, ClauseAnalysis, AnalysisReport)
  - `templatetags/` - Custom template filters for formatting
- `legal_classifier/` - ML model for risk classification
- `rag_pipeline/` - Retrieval-Augmented Generation components
- `user_auth/` - User authentication and authorization
- `templates/` - HTML templates with Bootstrap UI
- `static/` - CSS, JS, and other static files
- `media/` - Uploaded documents storage
- `data/legal_knowledge/` - Knowledge base for RAG pipeline

## Key Improvements

### Enhanced Clause Explanations
- Comprehensive English translations of legal terminology
- Support for multiple clause types (Termination, Payment, Confidentiality, Indemnification, Liability, Dispute Resolution, Non-Compete, IP, Governing Law, Amendments, Force Majeure, etc.)
- Automatic extraction of key information (amounts, durations, locations, notice periods)
- Legal language simplification (converts "shall" to "must", "pursuant to" to "according to", etc.)

### Comprehensive Executive Summaries
- Point-wise format with clear section headers
- Categorization of all clauses by type
- Detailed analysis of payment terms, termination conditions, liability provisions, etc.
- Risk considerations and recommendations
- Complete document overview with clause count

### Improved Risk Assessment
- Visual risk meter with accurate positioning
- Three-tier risk classification (Low, Medium, High)
- Detailed risk explanations for each clause
- Overall risk score calculation based on clause analysis

### Timezone Support
- All timestamps displayed in India/Kolkata timezone (IST)
- Timezone-aware datetime handling
- Clear timezone indicators in UI

### Running Tests

```
python manage.py test
```

## Acknowledgments

- Hugging Face for providing open-source models
- LangChain for the RAG pipeline framework
- Django community for the web framework 
