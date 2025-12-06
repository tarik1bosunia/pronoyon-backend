from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class Question(models.Model):
    """Base Question model supporting MCQ and Creative Questions"""
    
    # Question Types
    MCQ = 'mcq'
    CQ = 'cq'
    QUESTION_TYPE_CHOICES = [
        (MCQ, 'Multiple Choice Question'),
        (CQ, 'Creative Question'),
    ]
    
    # MCQ Subtypes
    SIMPLE = 'simple'
    COMBINED = 'combined'
    MCQ_SUBTYPE_CHOICES = [
        (SIMPLE, 'Simple MCQ (A, B, C, D)'),
        (COMBINED, 'Combined MCQ (i, ii, iii with choices)'),
    ]
    
    # Difficulty Levels
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    DIFFICULTY_CHOICES = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Question Type
    type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES)
    mcq_subtype = models.CharField(
        max_length=10,
        choices=MCQ_SUBTYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Only applicable for MCQ type"
    )
    
    # Content (supports Markdown and LaTeX)
    question_text = models.TextField(
        help_text="Question content with Markdown and LaTeX support"
    )
    question_text_html = models.TextField(
        blank=True,
        help_text="Rendered HTML version for caching"
    )
    
    # Marks and Difficulty
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default=MEDIUM
    )
    
    # Organization
    subject = models.ForeignKey(
        'questions.Subject',
        on_delete=models.CASCADE,
        related_name='questions'
    )
    topics = models.ManyToManyField(
        'questions.Topic',
        related_name='questions',
        blank=True
    )
    
    # Tags for flexible categorization
    tags = models.JSONField(default=list, blank=True)
    
    # Solution/Explanation
    solution = models.TextField(
        blank=True,
        help_text="Solution with Markdown and LaTeX support"
    )
    solution_html = models.TextField(blank=True)
    
    # Additional metadata
    hints = models.JSONField(
        default=list,
        blank=True,
        help_text="List of hints for students"
    )
    
    # Ownership and Permissions
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='questions_created',
        help_text="Manager who created this question"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="All questions are accessible to users by default"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether question has been reviewed and approved"
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions_verified'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        indexes = [
            models.Index(fields=['type', 'subject']),
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.question_text[:50]}"
