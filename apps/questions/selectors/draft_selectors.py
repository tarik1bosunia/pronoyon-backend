from django.db.models import Count, Prefetch, Q, QuerySet
from apps.questions.models import UserDraft, DraftQuestion, Question


class DraftSelectors:
    """Selectors for Draft models"""
    
    @staticmethod
    def get_user_drafts(user_id: str) -> QuerySet[UserDraft]:
        """Get all drafts for a user"""
        return UserDraft.objects.filter(user_id=user_id).order_by('-updated_at')
    
    @staticmethod
    def get_draft_by_id(draft_id: str, user_id: str) -> UserDraft:
        """Get draft by ID for a specific user"""
        return UserDraft.objects.get(id=draft_id, user_id=user_id)
    
    @staticmethod
    def get_draft_with_questions(draft_id: str, user_id: str) -> UserDraft:
        """Get draft with all questions"""
        return UserDraft.objects.prefetch_related(
            Prefetch(
                'draft_questions',
                queryset=DraftQuestion.objects.select_related(
                    'question',
                    'question__subject',
                    'question__subject__class_level'
                ).prefetch_related('question__topics').order_by('order')
            )
        ).get(id=draft_id, user_id=user_id)
    
    @staticmethod
    def get_favorite_drafts(user_id: str) -> QuerySet[UserDraft]:
        """Get favorite drafts for a user"""
        return UserDraft.objects.filter(
            user_id=user_id,
            is_favorite=True
        ).order_by('-updated_at')
    
    @staticmethod
    def search_user_drafts(user_id: str, search_term: str) -> QuerySet[UserDraft]:
        """Search user drafts by title or description"""
        return UserDraft.objects.filter(
            user_id=user_id
        ).filter(
            Q(title__icontains=search_term) | Q(description__icontains=search_term)
        ).order_by('-updated_at')
    
    @staticmethod
    def get_draft_questions(draft_id: str, user_id: str) -> QuerySet[DraftQuestion]:
        """Get all questions in a draft"""
        return DraftQuestion.objects.select_related(
            'draft',
            'question',
            'question__subject',
            'question__subject__class_level'
        ).prefetch_related(
            'question__topics'
        ).filter(
            draft_id=draft_id,
            draft__user_id=user_id
        ).order_by('order')
    
    @staticmethod
    def check_question_in_draft(draft_id: str, question_id: str, user_id: str) -> bool:
        """Check if a question exists in a draft"""
        return DraftQuestion.objects.filter(
            draft_id=draft_id,
            question_id=question_id,
            draft__user_id=user_id
        ).exists()
    
    @staticmethod
    def get_drafts_containing_question(user_id: str, question_id: str) -> QuerySet[UserDraft]:
        """Get all drafts that contain a specific question"""
        return UserDraft.objects.filter(
            user_id=user_id,
            draft_questions__question_id=question_id
        ).distinct().order_by('-updated_at')
