from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document, Clause, ClauseAnalysis, AnalysisReport
from .serializers import (
    DocumentSerializer, ClauseSerializer, ClauseAnalysisSerializer,
    AnalysisReportSerializer, DocumentDetailSerializer
)
from .forms import DocumentUploadForm
from .document_service import DocumentService

# Web UI Views
def index(request):
    """Home page view."""
    if request.user.is_authenticated:
        documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    else:
        documents = []
    return render(request, 'document_analyzer/index.html', {'documents': documents})

def upload_document(request):
    """View for uploading a new document."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to upload documents.')
        return redirect('login')
        
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            return redirect('document_analyzer:document_detail', pk=document.pk)
    else:
        form = DocumentUploadForm()
    return render(request, 'document_analyzer/upload.html', {'form': form})

@login_required
def document_detail(request, pk):
    """View for displaying document details and analysis."""
    document = get_object_or_404(Document, pk=pk, user=request.user)
    
    # Check if document needs processing
    if not document.processed:
        # Process the document
        DocumentService.process_document(document.id)
    
    clauses = document.clauses.all().order_by('position')
    return render(request, 'document_analyzer/document_detail.html', {
        'document': document,
        'clauses': clauses
    })

@login_required
def analysis_report(request, pk):
    """View for displaying the full analysis report."""
    document = get_object_or_404(Document, pk=pk, user=request.user)
    
    # Generate report if it doesn't exist
    try:
        report = document.report
    except AnalysisReport.DoesNotExist:
        result = DocumentService.generate_document_report(document.id)
        if result['success']:
            report = document.report
        else:
            report = None
    
    return render(request, 'document_analyzer/analysis_report.html', {
        'document': document,
        'report': report
    })

# API Views
class DocumentListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating documents."""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting a document."""
    serializer_class = DocumentDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

class ClauseDetailView(generics.RetrieveAPIView):
    """API view for retrieving a clause."""
    serializer_class = ClauseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Clause.objects.filter(document__user=self.request.user)

class ClauseAnalysisView(generics.RetrieveAPIView):
    """API view for retrieving clause analysis."""
    serializer_class = ClauseAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClauseAnalysis.objects.filter(clause__document__user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document(request, pk):
    """API endpoint to trigger document analysis."""
    document = get_object_or_404(Document, pk=pk, user=request.user)
    
    # Process and analyze the document
    result = DocumentService.analyze_document(document.id)
    
    return Response(result, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_clause(request, pk):
    """API endpoint to analyze a specific clause."""
    clause = get_object_or_404(Clause, pk=pk, document__user=request.user)
    
    # Analyze the clause
    result = DocumentService.analyze_clause(clause.id)
    
    return Response(result, status=status.HTTP_200_OK)
