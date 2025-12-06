from django.db import models
from django.conf import settings
import uuid


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
        'questions.Question',
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
