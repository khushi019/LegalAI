from django.urls import path
from . import views

app_name = 'document_analyzer'

urlpatterns = [
    # Web UI routes
    path('', views.index, name='index'),
    path('upload/', views.upload_document, name='upload'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/report/', views.analysis_report, name='analysis_report'),
    
    # API routes
    path('api/documents/', views.DocumentListCreateView.as_view(), name='api_document_list'),
    path('api/documents/<int:pk>/', views.DocumentDetailView.as_view(), name='api_document_detail'),
    path('api/documents/<int:pk>/analyze/', views.analyze_document, name='api_analyze_document'),
    path('api/clauses/<int:pk>/', views.ClauseDetailView.as_view(), name='api_clause_detail'),
    path('api/clauses/<int:pk>/analysis/', views.ClauseAnalysisView.as_view(), name='api_clause_analysis'),
] 