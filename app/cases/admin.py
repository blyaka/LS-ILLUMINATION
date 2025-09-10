from django.contrib import admin
from .models import Category, Case

class CaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order', 'photo')
    list_editable = ('order',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('order',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Case, CaseAdmin)
