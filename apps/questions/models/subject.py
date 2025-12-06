from django.db import models
from django.conf import settings
import uuid


class Subject(models.Model):
    """Subject/Course within a class, optionally within a group"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_level = models.ForeignKey(
        'questions.Class',
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="Class this subject belongs to"
    )
    group = models.ForeignKey(
        'questions.Group',
        on_delete=models.CASCADE,
        related_name='subjects',
        null=True,
        blank=True,
        help_text="Optional group (Science/Arts/Commerce) if the class has groups"
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
        ordering = ['class_level', 'group', 'order', 'name']
        unique_together = [['class_level', 'group', 'name']]
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        indexes = [
            models.Index(fields=['class_level', 'group', 'is_active']),
        ]
    
    def __str__(self):
        if self.group:
            return f"{self.class_level.name} - {self.group.name} - {self.name}"
        return f"{self.class_level.name} - {self.name}"
