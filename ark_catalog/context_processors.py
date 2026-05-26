def selection_count(request):
    """Calculates the number of items in the user's vault selection globally."""
    return {
        'selection_count': len(request.session.get('selection', []))
    }