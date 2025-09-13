from django.db import models

class Request(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=64)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} • {self.phone} • {self.created_at:%Y-%m-%d %H:%M}'



class ReqsRecipient(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    note = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = 'Получатель заявок'
        verbose_name_plural = 'Получатели заявок'
        ordering = ['-is_active', 'email']

    def __str__(self):
        return f'{self.email}{" (on)" if self.is_active else " (off)"}'