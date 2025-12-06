from django.db import models
from django.conf import settings
import uuid


class Subject(models.Model):
    """Subject/Course within a class"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_level = models.ForeignKey(
        'questions.Class',
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="Class this subject belongs to"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='subjects_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['class_level', 'order', 'name']
        unique_together = [['class_level', 'name']]
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return f"{self.class_level.name} - {self.name}"
