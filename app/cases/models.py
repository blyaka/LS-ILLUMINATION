from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class Category(models.Model):
    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)
    photo = models.ImageField('Фото', upload_to='portfolio/icons/', blank=True)
    icon = models.ImageField('Иконка', upload_to='portfolio/icons/', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Категория'
    )
    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)
    photo = models.ImageField('Фото', upload_to='portfolio/subcategories/', blank=True)
    icon = models.ImageField('Иконка', upload_to='portfolio/subcategories/', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        unique_together = [('category', 'name')]

    def __str__(self):
        return f'{self.category.name} → {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Case(models.Model):
    # Ветка 1: сразу в категорию (как сейчас)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='cases',          # это остаётся как было: category.cases — кейсы без подкатегорий
        verbose_name='Категория',
        null=True, blank=True
    )
    # Ветка 2: в подкатегорию
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='cases',          # subcategory.cases — кейсы в подкатегории
        verbose_name='Подкатегория',
        null=True, blank=True
    )

    slug = models.SlugField('Слаг', max_length=120, unique=True)
    name = models.CharField('Название', max_length=120)
    photo = models.ImageField('Фото', upload_to='portfolio/cases/')
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'
        constraints = [
            # Ровно одно из двух: category XOR subcategory
            models.CheckConstraint(
                name='case_category_xor_subcategory',
                check=(
                    (Q(category__isnull=False) & Q(subcategory__isnull=True)) |
                    (Q(category__isnull=True) & Q(subcategory__isnull=False))
                )
            ),
        ]
        indexes = [
            models.Index(fields=['category', 'order']),
            models.Index(fields=['subcategory', 'order']),
        ]

    def __str__(self):
        return self.name

    @property
    def resolved_category(self) -> Category:
        """Универсальный доступ к категории: либо прямая, либо через подкатегорию."""
        if self.category_id:
            return self.category
        return self.subcategory.category if self.subcategory_id else None

    def clean(self):
        # Доп. защита на уровне модели: не позволяй заполнить оба или ни одного
        if bool(self.category_id) == bool(self.subcategory_id):
            from django.core.exceptions import ValidationError
            raise ValidationError('У кейса должна быть либо категория, либо подкатегория (ровно одно).')

    def save(self, *args, **kwargs):
        # Если выбрана подкатегория — чистим прямую категорию, чтобы не ломать XOR
        if self.subcategory_id:
            self.category = None
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
