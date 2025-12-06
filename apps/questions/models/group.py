from django.db import models
from django.conf import settings
import uuid


class Group(models.Model):
    """Group/Stream within a class (e.g., Science, Arts, Commerce)"""
    
    # Common group types
    SCIENCE = 'science'
    ARTS = 'arts'
    COMMERCE = 'commerce'
    GENERAL = 'general'
    
    GROUP_TYPE_CHOICES = [
        (SCIENCE, 'Science'),
        (ARTS, 'Arts/Humanities'),
        (COMMERCE, 'Commerce/Business Studies'),
        (GENERAL, 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_level = models.ForeignKey(
        'questions.Class',
        on_delete=models.CASCADE,
        related_name='groups',
        help_text="Class this group belongs to"
    )
    name = models.CharField(max_length=100, help_text="e.g., Science, Arts, Commerce")
    code = models.CharField(max_length=20, null=True, blank=True)
    group_type = models.CharField(
        max_length=20,
        choices=GROUP_TYPE_CHOICES,
        default=GENERAL,
        help_text="Type of group"
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='groups_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['class_level', 'order', 'name']
        unique_together = [['class_level', 'name']]
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        indexes = [
            models.Index(fields=['class_level', 'is_active']),
            models.Index(fields=['group_type']),
        ]
    
    def __str__(self):
        return f"{self.class_level.name} - {self.name}"
