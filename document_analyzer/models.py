from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    """Model for storing uploaded legal documents."""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Clause(models.Model):
    """Model for storing individual clauses extracted from documents."""
    document = models.ForeignKey(Document, related_name='clauses', on_delete=models.CASCADE)
    text = models.TextField()
    page_number = models.IntegerField()
    position = models.IntegerField()  # Order of clause in document
    
    def __str__(self):
        return f"Clause {self.position} from {self.document}"

class ClauseAnalysis(models.Model):
    """Model for storing analysis results for each clause."""
    RISK_LEVELS = (
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    )
    
    clause = models.OneToOneField(Clause, related_name='analysis', on_delete=models.CASCADE)
    simplified_explanation = models.TextField()
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='low')
    risk_explanation = models.TextField(blank=True)
    keywords = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for {self.clause}"

class AnalysisReport(models.Model):
    """Model for storing overall document analysis reports."""
    document = models.OneToOneField(Document, related_name='report', on_delete=models.CASCADE)
    summary = models.TextField()
    risk_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report for {self.document}"
