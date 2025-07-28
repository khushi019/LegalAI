from rest_framework import serializers
from .models import Document, Clause, ClauseAnalysis, AnalysisReport

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'processed']
        read_only_fields = ['uploaded_at', 'processed']

class ClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clause
        fields = ['id', 'document', 'text', 'page_number', 'position']

class ClauseAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClauseAnalysis
        fields = ['id', 'clause', 'simplified_explanation', 'risk_level', 
                  'risk_explanation', 'keywords', 'created_at']
        read_only_fields = ['created_at']

class AnalysisReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisReport
        fields = ['id', 'document', 'summary', 'risk_score', 'created_at']
        read_only_fields = ['created_at']

class DocumentDetailSerializer(serializers.ModelSerializer):
    clauses = ClauseSerializer(many=True, read_only=True)
    report = AnalysisReportSerializer(read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'processed', 'clauses', 'report']
        read_only_fields = ['uploaded_at', 'processed'] 