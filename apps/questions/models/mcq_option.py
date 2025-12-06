from django.db import models
import uuid


class MCQOption(models.Model):
    """Options for Multiple Choice Questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='mcq_options'
    )
    
    # Option content
    option_text = models.TextField(
        help_text="Option text with Markdown and LaTeX support"
    )
    option_text_html = models.TextField(blank=True)
    
    # For simple MCQ: A, B, C, D
    # For combined MCQ: i, ii, iii, iv, v (statements)
    option_label = models.CharField(
        max_length=10,
        help_text="Label like 'A', 'B', or 'i', 'ii'"
    )
    
    # Answer marking
    is_correct = models.BooleanField(default=False)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # For combined MCQ: which statements are included in this choice
    combined_option_indices = models.JSONField(
        default=list,
        blank=True,
        help_text="For combined MCQ: list of statement indices"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question', 'order']
        verbose_name = 'MCQ Option'
        verbose_name_plural = 'MCQ Options'
    
    def __str__(self):
        return f"{self.option_label}. {self.option_text[:30]}"
