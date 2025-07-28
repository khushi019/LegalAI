from django import template

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