from django.contrib import admin
from .models import Category, Case

class CaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order', 'photo')
    list_editable = ('order',)
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('order',)
    prepopulated_fields = {"slug": ("name",)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug')
    list_editable = ('order',)
    list_display_links = ('name',)
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Case, CaseAdmin)
