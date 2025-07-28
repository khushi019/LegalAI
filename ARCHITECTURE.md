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
- **LLM Processor**: Generates plain English explanations of legal clauses
- **RAG Pipeline**: Provides legal context for clauses from a knowledge base
- **Risk Classifier**: Identifies potentially risky or unfair clauses

### Database
- SQLite for development (can be replaced with PostgreSQL for production)
- Stores documents, clauses, analyses, and reports

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
     - Plain English explanation is generated using LLM
     - Risk assessment is performed using the classifier
     - Analysis is saved to the database

4. **Report Generation**:
   - Overall risk score is calculated
   - Document summary is generated
   - Report is saved to the database

## Key Technologies

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML/CSS/JavaScript, Bootstrap
- **AI & NLP**: LangChain, Hugging Face Transformers
- **Vector Store**: FAISS for semantic search
- **PDF Parsing**: PyMuPDF, pdfplumber

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

## Future Enhancements

- Multi-language support
- Custom training of the risk classifier
- Collaborative document review
- Integration with document management systems
- Mobile application 