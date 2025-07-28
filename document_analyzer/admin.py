from django.contrib import admin
from .models import Document, Clause

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'user', 'processed')
    list_filter = ('processed', 'uploaded_at')
    search_fields = ('title', 'user__username')

@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ('document', 'page_number', 'position')
    list_filter = ('page_number',)
    search_fields = ('text', 'document__title')
