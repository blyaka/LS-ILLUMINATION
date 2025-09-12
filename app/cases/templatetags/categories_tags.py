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

@register.simple_tag
def next_category(categories, current):
    """
    Возвращает следующую категорию из уже отсортированного списка categories (по order).
    Без доп. SQL: работаем по списку из контекст-процессора.
    """
    if not categories or not current:
        return None
    cat_list = list(categories)
    # ищем по pk, а не по объекту на всякий
    try:
        idx = next(i for i, c in enumerate(cat_list) if c.pk == current.pk)
    except StopIteration:
        return None
    return cat_list[(idx + 1) % len(cat_list)]