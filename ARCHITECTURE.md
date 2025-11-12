# LegalDoc AI - System Architecture

This document provides an overview of the LegalDoc AI system architecture and components.

## System Overview

LegalDoc AI is a full-stack application that enables users to upload legal documents and receive clause-by-clause explanations in plain English along with risk analysis. The system combines natural language processing, retrieval-augmented generation, large language models, and machine learning-based classification.

## Architecture Diagram

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Web Interface   |<--->|  Django Backend  |<--->|  AI Components   |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                 ^
                                 |
                                 v
                         +------------------+
                         |                  |
                         |    Database      |
                         |                  |
                         +------------------+
```

## Components

### Web Interface
- HTML/CSS/JavaScript frontend
- Bootstrap for responsive design
- Django templates for server-side rendering
- AJAX for asynchronous processing

### Django Backend
- Django web framework
- Django REST Framework for API endpoints
- Authentication and authorization
- Document storage and management
- PDF processing and clause extraction

### AI Components
- **LLM Processor**: Generates comprehensive plain English explanations of legal clauses
  - Enhanced fallback explanation system with detailed translations
  - Support for multiple clause types (Termination, Payment, Confidentiality, Indemnification, Liability, etc.)
  - Automatic extraction of key information (amounts, durations, locations)
  - Legal language simplification
- **Document Summarizer**: Generates point-wise executive summaries
  - Categorizes clauses by type
  - Provides comprehensive analysis of all document sections
  - Risk considerations and recommendations
- **RAG Pipeline**: Provides legal context for clauses from a knowledge base
- **Risk Classifier**: Identifies potentially risky or unfair clauses
  - Three-tier classification (Low, Medium, High)
  - Keyword-based and ML-based risk detection

### Database
- SQLite for development (can be replaced with PostgreSQL for production)
- Stores documents, clauses, analyses, and reports
- Timezone-aware datetime fields (configured for Asia/Kolkata - IST)

## Data Flow

1. **Document Upload**:
   - User uploads a PDF document
   - Document is saved to the database
   - Document processing is initiated

2. **Document Processing**:
   - PDF is parsed and text is extracted
   - Text is split into clauses based on patterns
   - Clauses are saved to the database

3. **Clause Analysis**:
   - For each clause:
     - Legal context is retrieved using RAG
     - Enhanced plain English explanation is generated
       - Comprehensive translations of legal terminology
       - Extraction of key information (amounts, durations, locations)
       - Language simplification for better understanding
     - Risk assessment is performed using the classifier
       - Keyword-based detection
       - ML-based classification
       - Risk level assignment (Low/Medium/High)
     - Analysis is saved to the database

4. **Report Generation**:
   - Overall risk score is calculated from clause analyses
   - Comprehensive point-wise executive summary is generated
     - Document overview with clause count
     - Categorized analysis by clause type
     - Detailed breakdown of key terms
     - Risk considerations
   - Report is saved to the database with timestamps in IST

## Key Technologies

- **Backend**: Django 5.2.4, Django REST Framework
- **Frontend**: HTML/CSS/JavaScript, Bootstrap
- **AI & NLP**: 
  - LangChain (with HuggingFace integration)
  - Hugging Face Transformers (google/flan-t5-small)
  - Sentence Transformers for embeddings
- **Vector Store**: FAISS for semantic search
- **PDF Parsing**: PyMuPDF, pdfplumber
- **ML & Classification**: scikit-learn, PyTorch
- **Timezone**: Asia/Kolkata (IST) for all timestamps

## API Endpoints

- `POST /api/documents/`: Upload a new document
- `GET /api/documents/`: List all documents
- `GET /api/documents/{id}/`: Get document details
- `POST /api/documents/{id}/analyze/`: Analyze a document
- `GET /api/clauses/{id}/`: Get clause details
- `POST /api/clauses/{id}/analysis/`: Analyze a clause

## Security Considerations

- Authentication required for all operations
- Document access restricted to owners
- Sensitive data not stored in plaintext
- Input validation for all API endpoints
- Timezone-aware datetime handling

## Recent Improvements

### Enhanced Clause Explanations
- Comprehensive English translations instead of generic "consult legal advisor" messages
- Support for 15+ clause types with detailed explanations
- Automatic extraction of amounts, durations, notice periods, and locations
- Legal language simplification (shall → must, pursuant to → according to, etc.)

### Comprehensive Executive Summaries
- Point-wise format with clear section headers
- Complete analysis of all clauses (not just first 5)
- Categorization by clause type
- Detailed breakdown of payment terms, termination conditions, liability provisions
- Risk considerations and recommendations

### Improved Risk Assessment UI
- Visual risk meter with accurate positioning (0-100% scale)
- Three-tier risk classification with detailed explanations
- Overall risk score calculation based on clause analysis

### Timezone Support
- All timestamps displayed in India/Kolkata timezone (IST)
- Timezone-aware datetime fields
- Clear timezone indicators in user interface

## Future Enhancements

- Multi-language support
- Custom training of the risk classifier
- Collaborative document review
- Integration with document management systems
- Mobile application
- Advanced LLM integration for even better explanations 