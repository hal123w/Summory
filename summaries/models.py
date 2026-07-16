from django.conf import settings
from django.db import models


class Summary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='summaries',
    )
    title = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text='任意。1つまで。空なら「すべて」にのみ表示。',
    )
    original_text = models.TextField()
    summary_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name_plural = 'summaries'

    def __str__(self):
        return self.title or f'Summary {self.pk}'

    def display_title(self):
        if self.title.strip():
            return self.title.strip()
        first_line = self.summary_text.strip().splitlines()[0] if self.summary_text.strip() else '無題'
        return first_line[:60]
