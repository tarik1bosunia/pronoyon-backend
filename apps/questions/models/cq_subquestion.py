from django.db import models
from decimal import Decimal
import uuid


class CQSubQuestion(models.Model):
    """Sub-questions for Creative Questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='cq_sub_questions'
    )
    
    # Sub-question identifier (a, b, c, etc.)
    label = models.CharField(max_length=10, help_text="Label like 'a', 'b', 'c'")
    
    # Content
    sub_question_text = models.TextField(
        help_text="Sub-question text with Markdown and LaTeX support"
    )
    sub_question_text_html = models.TextField(blank=True)
    
    # Marks for this sub-question
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    
    # Answer/Solution
    answer = models.TextField(
        blank=True,
        help_text="Answer with Markdown and LaTeX support"
    )
    answer_html = models.TextField(blank=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question', 'order']
        unique_together = [['question', 'label']]
        verbose_name = 'CQ Sub-Question'
        verbose_name_plural = 'CQ Sub-Questions'
    
    def __str__(self):
        return f"{self.label}. {self.sub_question_text[:30]}"
