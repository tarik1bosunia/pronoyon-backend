from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


class Subject(models.Model):
    """Subject/Course for categorizing questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    
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
        ordering = ['name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    """Topic/Chapter within a subject"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
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
        ordering = ['subject', 'order', 'name']
        unique_together = [['subject', 'name']]
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"


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
        Subject,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    topics = models.ManyToManyField(
        Topic,
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


class MCQOption(models.Model):
    """Options for Multiple Choice Questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
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


class CQSubQuestion(models.Model):
    """Sub-questions for Creative Questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
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


class UserDraft(models.Model):
    """User's personal draft/collection of questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='drafts'
    )
    
    # Draft details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Draft metadata
    is_favorite = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'User Draft'
        verbose_name_plural = 'User Drafts'
        unique_together = [['user', 'title']]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    @property
    def question_count(self):
        return self.draft_questions.count()


class DraftQuestion(models.Model):
    """Questions added to a user's draft"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.ForeignKey(
        UserDraft,
        on_delete=models.CASCADE,
        related_name='draft_questions'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='in_drafts'
    )
    
    # Order within draft
    order = models.PositiveIntegerField(default=0)
    
    # User notes for this question
    notes = models.TextField(blank=True)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['draft', 'order']
        unique_together = [['draft', 'question']]
        verbose_name = 'Draft Question'
        verbose_name_plural = 'Draft Questions'
    
    def __str__(self):
        return f"{self.draft.title} - Q{self.order}"
