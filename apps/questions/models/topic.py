from django.db import models
from django.conf import settings
import uuid


class Topic(models.Model):
    """Topic within a chapter"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(
        'questions.Chapter',
        on_delete=models.CASCADE,
        related_name='topics',
        help_text="Chapter this topic belongs to"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='topics_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['chapter', 'order', 'name']
        unique_together = [['chapter', 'name']]
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
    
    def __str__(self):
        return f"{self.chapter.name} - {self.name}"
