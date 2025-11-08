from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def filter_by_risk(clauses, risk_level):
    """Filter clauses by risk level."""
    return [clause for clause in clauses if hasattr(clause, 'analysis') and 
            clause.analysis and clause.analysis.risk_level == risk_level]

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def format_summary(value):
    """Format the executive summary with point-wise formatting."""
    if not value:
        return ""
    
    # Split by double newlines to get paragraphs
    paragraphs = value.split('\n\n')
    formatted_html = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if paragraph starts with ** (bold header)
        if para.startswith('**') and ':**' in para:
            # Extract the header and content
            match = re.match(r'\*\*(.*?):\*\*\s*(.*)', para)
            if match:
                header = match.group(1)
                content = match.group(2).strip()
                # Format as a paragraph with bold header
                formatted_html.append(f'<p class="mb-3"><strong>{header}:</strong> {content}</p>')
            else:
                # Fallback: just remove ** and format
                para_clean = para.replace('**', '')
                formatted_html.append(f'<p class="mb-3">{para_clean}</p>')
        else:
            # Regular paragraph
            para_clean = para.replace('**', '')
            formatted_html.append(f'<p class="mb-3">{para_clean}</p>')
    
    return mark_safe('\n'.join(formatted_html)) 