"""Analyseur de risque pour les échantillons texte et fichiers."""

def assess(features, score):
    """Renvoie un niveau de risque textuel à partir du score et des features."""
    if score >= 0.75:
        return 'high'
    if score >= 0.45:
        return 'medium'
    if features.get('is_pe') or features.get('suspicious_extension') or features.get('suspicious_hits', 0) > 0:
        return 'medium'
    return 'low'
