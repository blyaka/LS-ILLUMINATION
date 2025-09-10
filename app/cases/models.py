from django.db import models

class Category(models.Model):
    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Case(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cases', verbose_name='Категория')
    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)
    photo = models.ImageField('Фото', upload_to='cases/')
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'

    def __str__(self):
        return self.name