from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from .models import Video, News
from django.utils.module_loading import import_string
import threading

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('name','is_featured','status','created','preview','m3u8_link')
    list_filter  = ('status','is_featured')
    list_editable = ('is_featured',)
    readonly_fields = ('status','m3u8_url','out_dir','meta','error','created','preview_tag')
    fields = ('name','source','is_featured','status','preview_tag','m3u8_url','out_dir','meta','error','created')

    def preview(self, obj):
        return format_html('<img src="{}" style="height:60px;border-radius:6px"/>', obj.poster.url) if obj.poster else '-'

    def m3u8_link(self, obj):
        return format_html('<a href="{}" target="_blank">m3u8</a>', obj.m3u8_url) if obj.m3u8_url else '-'

    def preview_tag(self, obj):
        return self.preview(obj)
    preview_tag.short_description = 'Постер'

    def get_urls(self):
        urls = super().get_urls()
        return [path('<uuid:pk>/rebuild/', self.admin_site.admin_view(self.rebuild), name='content_video_rebuild')] + urls

    def rebuild(self, request, pk):
        try:
            v = Video.objects.get(pk=pk)
            v.status = Video.S.QUEUED
            v.save(update_fields=['status'])
            threading.Thread(target=lambda: import_string('content.services.process_video')(str(v.pk)),
                     daemon=True).start()
            self.message_user(request, 'Переконвертация запущена', messages.INFO)
        except Exception as e:
            self.message_user(request, f'Ошибка: {e}', messages.ERROR)
        return redirect(f'../../{pk}/change/')




@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    list_filter  = ("created_at",)
    search_fields = ("title", "text")
    date_hierarchy = "created_at"