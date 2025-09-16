import os, uuid, json, threading, subprocess, shlex
from django.db import models, transaction
from django.db.models import Q, Max
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string
from django.apps import apps

class Video(models.Model):
    class S:
        QUEUED='queued'; PROC='processing'; READY='ready'; FAIL='failed'
        CHOICES=[(QUEUED,'В очереди'),(PROC,'Обработка'),(READY,'Готово'),(FAIL,'Ошибка')]

    class P:
        HERO='hero'; GALLERY='gallery'; BLOCK='block'
        CHOICES=[(HERO,'Hero'),(GALLERY,'Видеогалерея'),(BLOCK,'Видеоблок')]

    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name     = models.CharField('Название', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True, null=True)
    source   = models.FileField('Исходник', upload_to='video/source/')
    placement= models.CharField('Размещение', max_length=12, choices=P.CHOICES, default=P.GALLERY, db_index=True)
    position = models.PositiveIntegerField('Порядок в группе', default=0, db_index=True,
                                           help_text='Работает для видеогалереи и видеоблока')
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
        ordering = ('placement','position','-created')
        constraints = [
            models.UniqueConstraint(
                fields=['placement'],
                condition=Q(placement='hero'),
                name='only_one_hero_video'
            ),
            models.UniqueConstraint(
                fields=['placement','position'],
                condition=Q(position__gt=0),
                name='unique_position_per_group'
            ),
        ]

    def __str__(self):
        return self.name or os.path.basename(self.source.name)

    @property
    def abs_out_dir(self):
        rel = self.out_dir or f'video/{self.id}/'
        return os.path.join(settings.MEDIA_ROOT, rel)

    @property
    def rel_out_dir(self):
        return self.out_dir or f'video/{self.id}/'

    def _ensure_position(self):
        if self.placement in (self.P.GALLERY, self.P.BLOCK) and not self.position:
            last = type(self).objects.filter(placement=self.placement).aggregate(m=Max('position'))['m'] or 0
            self.position = last + 1
        if self.placement == self.P.HERO:
            self.position = 0

    def save(self, *args, **kwargs):
        is_create = self._state.adding
        prev_placement = None
        if not is_create:
            prev_placement = type(self).objects.only('placement').get(pk=self.pk).placement

        self._ensure_position()
        super().save(*args, **kwargs)

        if self.placement == self.P.HERO:
            type(self).objects.exclude(pk=self.pk).filter(placement=self.P.HERO)\
                .update(placement=self.P.GALLERY)

        if is_create and self.source:
            type(self).objects.filter(pk=self.pk).update(
                status=self.S.QUEUED, error='', out_dir=f'video/{self.pk}/'
            )
            def run():
                try:
                    import_string('content.services.process_video')(str(self.pk))
                except Exception as e:
                    apps.get_model('content','Video').objects.filter(pk=self.pk).update(
                        status=self.S.FAIL, error=str(e)
                    )
            threading.Thread(target=run, daemon=True).start()





class News(models.Model):
    title = models.CharField("Название", max_length=255)
    image = models.ImageField("Фото", upload_to="news/%Y/%m/")
    text = models.TextField("Текст")
    is_available = models.BooleanField('Показывать на главной', default=True)
    created_at = models.DateTimeField("Дата создания", default=timezone.now)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title
    


class PDFFile(models.Model):
    name = models.CharField('Название', max_length=50)
    file = models.FileField('ПДФ', upload_to='pdf/')

    class Meta:
        verbose_name = 'PDF файл'
        verbose_name_plural = 'PDF файлы'

    def __str__(self):
        return self.name