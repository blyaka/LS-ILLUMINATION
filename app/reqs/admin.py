from django.contrib import admin
from .models import Request, ReqsRecipient

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('name','phone','email','created_at')
    search_fields = ('name','phone','email','message')
    list_filter = ('created_at',)

@admin.register(ReqsRecipient)
class ReqsRecipientAdmin(admin.ModelAdmin):
    list_display = ('email','is_active','note')
    list_editable = ('is_active',)
    search_fields = ('email','note')
