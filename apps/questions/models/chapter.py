from django.db import models
from django.conf import settings
import uuid


class Chapter(models.Model):
    """Chapter within a subject"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        'questions.Subject',
        on_delete=models.CASCADE,
        related_name='chapters',
        help_text="Subject this chapter belongs to"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='chapters_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['subject', 'order', 'name']
        unique_together = [['subject', 'name']]
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"
