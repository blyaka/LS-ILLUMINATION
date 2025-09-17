from django.contrib import admin
from .models import Category, Subcategory, Case


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    fields = ('name', 'order', 'slug')
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug')
    list_editable = ('order',)
    list_display_links = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    inlines = [SubcategoryInline]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order', 'slug')
    list_editable = ('order',)
    list_display_links = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_category', 'get_subcategory', 'order', 'photo')
    list_editable = ('order',)
    list_filter = ('category', 'subcategory')
    search_fields = ('name',)
    ordering = ('order',)
    prepopulated_fields = {"slug": ("name",)}

    def get_category(self, obj):
        return obj.category or (obj.subcategory.category if obj.subcategory else None)
    get_category.short_description = "Категория"

    def get_subcategory(self, obj):
        return obj.subcategory
    get_subcategory.short_description = "Подкатегория"
