from django.db import models
from django.conf import settings
import uuid


class Class(models.Model):
    """Class/Grade level (e.g., Class 6, Class 7, HSC, Admission, etc.)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Class 6, Class 7, HSC, Admission")
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    has_groups = models.BooleanField(
        default=False,
        help_text="Whether this class has groups (Science, Arts, Commerce). Typically True for HSC and Admission."
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='classes_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return self.name
