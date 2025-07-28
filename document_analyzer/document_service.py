from .models import Document, Clause, ClauseAnalysis, AnalysisReport
from .pdf_processor import process_document
from .llm_processor import explain_legal_clause, summarize_legal_document
from rag_pipeline.rag_processor import get_legal_context_for_clause
from legal_classifier.risk_classifier import classify_clause_risk
from typing import Dict, Any

class DocumentService:
    """Service for processing and analyzing legal documents."""
    
    @staticmethod
    def process_document(document_id: int) -> Dict[str, Any]:
        """Process a document and extract clauses."""
        try:
            # Get the document
            document = Document.objects.get(pk=document_id)
            
            # Process the document to extract clauses
            extracted_clauses = process_document(document)
            
            # Save the extracted clauses
            clauses = []
            for clause_data in extracted_clauses:
                clause = Clause.objects.create(
                    document=document,
                    text=clause_data['text'],
                    page_number=clause_data['page_number'],
                    position=clause_data['position']
                )
                clauses.append(clause)
            
            # Mark the document as processed
            document.processed = True
            document.save()
            
            return {
                'success': True,
                'message': f'Successfully processed document and extracted {len(clauses)} clauses.',
                'document_id': document_id,
                'clauses': [{'id': c.id, 'position': c.position} for c in clauses]
            }
        except Document.DoesNotExist:
            return {
                'success': False,
                'message': f'Document with ID {document_id} not found.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing document: {str(e)}'
            }
    
    @staticmethod
    def analyze_clause(clause_id: int) -> Dict[str, Any]:
        """Analyze a clause using LLM, RAG, and risk classification."""
        try:
            # Get the clause
            clause = Clause.objects.get(pk=clause_id)
            
            # Get legal context using RAG
            legal_context = get_legal_context_for_clause(clause.text)
            
            # Classify risk
            risk_analysis = classify_clause_risk(clause.text)
            
            # Generate explanation
            explanation = explain_legal_clause(clause.text, legal_context)
            
            # Save the analysis
            analysis = ClauseAnalysis.objects.create(
                clause=clause,
                simplified_explanation=explanation,
                risk_level=risk_analysis['risk_level'],
                risk_explanation=risk_analysis['explanation'],
                keywords=risk_analysis['keywords']
            )
            
            return {
                'success': True,
                'message': 'Successfully analyzed clause.',
                'clause_id': clause_id,
                'analysis_id': analysis.id,
                'explanation': explanation,
                'risk_level': risk_analysis['risk_level'],
                'risk_explanation': risk_analysis['explanation']
            }
        except Clause.DoesNotExist:
            return {
                'success': False,
                'message': f'Clause with ID {clause_id} not found.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error analyzing clause: {str(e)}'
            }
    
    @staticmethod
    def generate_document_report(document_id: int) -> Dict[str, Any]:
        """Generate an overall report for the document."""
        try:
            # Get the document
            document = Document.objects.get(pk=document_id)
            
            # Get all clauses
            clauses = Clause.objects.filter(document=document).order_by('position')
            
            if not clauses:
                return {
                    'success': False,
                    'message': 'No clauses found for this document.'
                }
            
            # Get all analyses
            analyses = []
            for clause in clauses:
                try:
                    analysis = ClauseAnalysis.objects.get(clause=clause)
                    analyses.append({
                        'clause_id': clause.id,
                        'risk_level': analysis.risk_level,
                        'explanation': analysis.simplified_explanation
                    })
                except ClauseAnalysis.DoesNotExist:
                    continue
            
            # Calculate overall risk score
            risk_scores = {'low': 0, 'medium': 1, 'high': 2}
            if analyses:
                avg_risk_score = sum(risk_scores[a['risk_level']] for a in analyses) / len(analyses)
            else:
                avg_risk_score = 0
            
            # Generate document summary
            clause_texts = [{'text': c.text} for c in clauses]
            summary = summarize_legal_document(clause_texts)
            
            # Create or update report
            try:
                report = AnalysisReport.objects.get(document=document)
                report.summary = summary
                report.risk_score = avg_risk_score
                report.save()
            except AnalysisReport.DoesNotExist:
                report = AnalysisReport.objects.create(
                    document=document,
                    summary=summary,
                    risk_score=avg_risk_score
                )
            
            return {
                'success': True,
                'message': 'Successfully generated document report.',
                'document_id': document_id,
                'report_id': report.id,
                'summary': summary,
                'risk_score': avg_risk_score,
                'analyses_count': len(analyses)
            }
        except Document.DoesNotExist:
            return {
                'success': False,
                'message': f'Document with ID {document_id} not found.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating document report: {str(e)}'
            }
    
    @staticmethod
    def analyze_document(document_id: int) -> Dict[str, Any]:
        """Process and analyze an entire document."""
        # Process the document
        process_result = DocumentService.process_document(document_id)
        if not process_result['success']:
            return process_result
        
        # Analyze each clause
        clauses = process_result.get('clauses', [])
        for clause in clauses:
            DocumentService.analyze_clause(clause['id'])
        
        # Generate report
        report_result = DocumentService.generate_document_report(document_id)
        
        return {
            'success': True,
            'message': 'Document processing and analysis complete.',
            'document_id': document_id,
            'clauses_processed': len(clauses),
            'report': report_result if report_result['success'] else None
        } 