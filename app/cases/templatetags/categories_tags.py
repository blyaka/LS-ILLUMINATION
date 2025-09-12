from django import template

register = template.Library()

@register.filter
def chunk_categories(categories, pattern=(5, 4)):
    """
    Разбивает список категорий на ряды: сначала 5, потом 4, потом снова 5 и т.д.
    """
    result = []
    i = 0
    p = list(pattern)
    while i < len(categories):
        for size in p:
            if i >= len(categories):
                break
            result.append(categories[i:i+size])
            i += size
    return result
