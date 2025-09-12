from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)
    photo = models.ImageField('Фото', upload_to='portfolio/icons/', blank=True)
    icon = models.ImageField('Иконка', upload_to='portfolio/icons/', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Case(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cases', verbose_name='Категория')
    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)
    photo = models.ImageField('Фото', upload_to='portfolio/cases/')
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)