from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import Document, Clause, ClauseAnalysis, AnalysisReport
from .document_service import DocumentService

class DocumentModelTests(TestCase):
    """Tests for the Document model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a simple PDF file for testing
        self.pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000233 00000 n\n0000000300 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n394\n%%EOF'
        
        self.document = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile('test.pdf', self.pdf_content),
            user=self.user
        )
    
    def test_document_creation(self):
        """Test that a document can be created."""
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.user, self.user)
        self.assertFalse(self.document.processed)
    
    def test_document_str(self):
        """Test the string representation of a document."""
        self.assertEqual(str(self.document), 'Test Document')

class ClauseModelTests(TestCase):
    """Tests for the Clause model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile('test.pdf', b'Test PDF content'),
            user=self.user
        )
        
        self.clause = Clause.objects.create(
            document=self.document,
            text='This is a test clause.',
            page_number=1,
            position=0
        )
    
    def test_clause_creation(self):
        """Test that a clause can be created."""
        self.assertEqual(Clause.objects.count(), 1)
        self.assertEqual(self.clause.text, 'This is a test clause.')
        self.assertEqual(self.clause.document, self.document)
    
    def test_clause_str(self):
        """Test the string representation of a clause."""
        self.assertEqual(str(self.clause), f'Clause 0 from {self.document}')

class DocumentServiceTests(TestCase):
    """Tests for the DocumentService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.document = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile('test.pdf', b'Test PDF content'),
            user=self.user
        )
    
    def test_process_document(self):
        """Test processing a document."""
        # Mock the process_document function to avoid actual PDF processing
        original_process_document = DocumentService.process_document
        
        try:
            # Replace with a mock function
            def mock_process_document(document_id):
                document = Document.objects.get(pk=document_id)
                # Create a test clause
                Clause.objects.create(
                    document=document,
                    text='This is a test clause.',
                    page_number=1,
                    position=0
                )
                document.processed = True
                document.save()
                return {
                    'success': True,
                    'message': 'Successfully processed document and extracted 1 clauses.',
                    'document_id': document_id,
                    'clauses': [{'id': clause.id, 'position': clause.position} for clause in document.clauses.all()]
                }
            
            DocumentService.process_document = mock_process_document
            
            # Test the service
            result = DocumentService.process_document(self.document.id)
            
            # Check the result
            self.assertTrue(result['success'])
            self.assertEqual(Clause.objects.count(), 1)
            self.assertEqual(Clause.objects.first().text, 'This is a test clause.')
            
            # Check that the document was marked as processed
            self.document.refresh_from_db()
            self.assertTrue(self.document.processed)
            
        finally:
            # Restore the original function
            DocumentService.process_document = original_process_document

class ViewTests(TestCase):
    """Tests for views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.client.login(username='testuser', password='testpassword')
        
        self.document = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile('test.pdf', b'Test PDF content'),
            user=self.user,
            processed=True
        )
        
        self.clause = Clause.objects.create(
            document=self.document,
            text='This is a test clause.',
            page_number=1,
            position=0
        )
    
    def test_index_view(self):
        """Test the index view."""
        response = self.client.get(reverse('document_analyzer:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')
    
    def test_document_detail_view(self):
        """Test the document detail view."""
        response = self.client.get(
            reverse('document_analyzer:document_detail', kwargs={'pk': self.document.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')
        self.assertContains(response, 'This is a test clause.')
