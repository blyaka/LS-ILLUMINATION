import os, uuid, json, threading, subprocess, shlex
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string
from django.apps import apps

class Video(models.Model):
    class S:
        QUEUED = 'queued'
        PROC   = 'processing'
        READY  = 'ready'
        FAIL   = 'failed'
        CHOICES = [(QUEUED,'В очереди'),(PROC,'Обработка'),(READY,'Готово'),(FAIL,'Ошибка')]

    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name     = models.CharField('Название', max_length=200, blank=True)
    source   = models.FileField('Исходник', upload_to='video/source/')
    status   = models.CharField('Статус', max_length=16, choices=S.CHOICES, default=S.QUEUED, db_index=True)
    poster   = models.ImageField('Постер', upload_to='video/posters/', blank=True, null=True)
    m3u8_url = models.CharField('Плейлист HLS', max_length=500, blank=True)
    out_dir  = models.CharField('Папка результата', max_length=500, blank=True)
    meta     = models.JSONField('Мета', default=dict, blank=True)
    error    = models.TextField('Ошибка', blank=True)
    created  = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
        ordering = ['-created']

    def __str__(self):
        return self.name or os.path.basename(self.source.name)

    @property
    def abs_out_dir(self):
        rel = self.out_dir or f'video/{self.id}/'
        return os.path.join(settings.MEDIA_ROOT, rel)

    @property
    def rel_out_dir(self):
        return self.out_dir or f'video/{self.id}/'


    def save(self, *args, **kwargs):
        new_file = ...
        super().save(*args, **kwargs)
        if new_file and self.source:
            self.status = self.S.QUEUED
            self.error = ''
            self.out_dir = f'video/{self.id}/'
            super().save(update_fields=['status','error','out_dir'])

            def run():
                try:
                    process_video = import_string('content.services.process_video')
                    process_video(str(self.pk))
                except Exception as e:
                    Video = apps.get_model('content', 'Video')
                    Video.objects.filter(pk=self.pk).update(status=self.S.FAIL, error=str(e))

            transaction.on_commit(lambda: threading.Thread(target=run, daemon=True).start())
