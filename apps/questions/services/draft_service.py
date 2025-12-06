from typing import Dict, Any, List
from django.db import transaction
from apps.questions.models import UserDraft, DraftQuestion


class DraftService:
    """Service for Draft model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_draft(*, user, data: Dict[str, Any]) -> UserDraft:
        """Create a new draft"""
        draft = UserDraft.objects.create(
            user=user,
            title=data['title'],
            description=data.get('description', ''),
            is_favorite=data.get('is_favorite', False)
        )
        return draft
    
    @staticmethod
    @transaction.atomic
    def update_draft(*, draft_id: str, user_id: str, data: Dict[str, Any]) -> UserDraft:
        """Update a draft"""
        draft = UserDraft.objects.get(id=draft_id, user_id=user_id)
        
        if 'title' in data:
            draft.title = data['title']
        if 'description' in data:
            draft.description = data['description']
        if 'is_favorite' in data:
            draft.is_favorite = data['is_favorite']
        
        draft.save()
        return draft
    
    @staticmethod
    @transaction.atomic
    def delete_draft(*, draft_id: str, user_id: str) -> None:
        """Delete a draft"""
        draft = UserDraft.objects.get(id=draft_id, user_id=user_id)
        draft.delete()
    
    @staticmethod
    @transaction.atomic
    def add_question_to_draft(
        *,
        draft_id: str,
        user_id: str,
        question_id: str,
        notes: str = ''
    ) -> DraftQuestion:
        """Add a question to a draft"""
        draft = UserDraft.objects.get(id=draft_id, user_id=user_id)
        
        # Get the next order number
        max_order = DraftQuestion.objects.filter(draft=draft).count()
        
        # Check if question already exists in draft
        existing = DraftQuestion.objects.filter(
            draft=draft,
            question_id=question_id
        ).first()
        
        if existing:
            return existing
        
        draft_question = DraftQuestion.objects.create(
            draft=draft,
            question_id=question_id,
            order=max_order,
            notes=notes
        )
        
        return draft_question
    
    @staticmethod
    @transaction.atomic
    def add_multiple_questions_to_draft(
        *,
        draft_id: str,
        user_id: str,
        question_ids: List[str]
    ) -> List[DraftQuestion]:
        """Add multiple questions to a draft"""
        draft = UserDraft.objects.get(id=draft_id, user_id=user_id)
        
        # Get existing question IDs
        existing_ids = set(
            DraftQuestion.objects.filter(draft=draft).values_list('question_id', flat=True)
        )
        
        # Filter out already added questions
        new_question_ids = [qid for qid in question_ids if qid not in existing_ids]
        
        # Get the starting order number
        max_order = DraftQuestion.objects.filter(draft=draft).count()
        
        # Create draft questions
        draft_questions = []
        for idx, question_id in enumerate(new_question_ids):
            draft_question = DraftQuestion.objects.create(
                draft=draft,
                question_id=question_id,
                order=max_order + idx
            )
            draft_questions.append(draft_question)
        
        return draft_questions
    
    @staticmethod
    @transaction.atomic
    def remove_question_from_draft(
        *,
        draft_id: str,
        user_id: str,
        question_id: str
    ) -> None:
        """Remove a question from a draft"""
        DraftQuestion.objects.filter(
            draft_id=draft_id,
            draft__user_id=user_id,
            question_id=question_id
        ).delete()
        
        # Reorder remaining questions
        draft_questions = DraftQuestion.objects.filter(
            draft_id=draft_id
        ).order_by('order')
        
        for idx, dq in enumerate(draft_questions):
            if dq.order != idx:
                dq.order = idx
                dq.save(update_fields=['order'])
    
    @staticmethod
    @transaction.atomic
    def update_draft_question_notes(
        *,
        draft_id: str,
        user_id: str,
        question_id: str,
        notes: str
    ) -> DraftQuestion:
        """Update notes for a question in draft"""
        draft_question = DraftQuestion.objects.get(
            draft_id=draft_id,
            draft__user_id=user_id,
            question_id=question_id
        )
        draft_question.notes = notes
        draft_question.save()
        return draft_question
    
    @staticmethod
    @transaction.atomic
    def reorder_draft_questions(
        *,
        draft_id: str,
        user_id: str,
        question_orders: List[Dict[str, Any]]
    ) -> None:
        """Reorder questions in a draft
        
        Args:
            draft_id: The draft ID
            user_id: The user ID
            question_orders: List of dicts with 'question_id' and 'order' keys
        """
        for item in question_orders:
            DraftQuestion.objects.filter(
                draft_id=draft_id,
                draft__user_id=user_id,
                question_id=item['question_id']
            ).update(order=item['order'])
    
    @staticmethod
    @transaction.atomic
    def toggle_draft_favorite(*, draft_id: str, user_id: str) -> UserDraft:
        """Toggle favorite status of a draft"""
        draft = UserDraft.objects.get(id=draft_id, user_id=user_id)
        draft.is_favorite = not draft.is_favorite
        draft.save()
        return draft
    
    @staticmethod
    @transaction.atomic
    def clear_draft(*, draft_id: str, user_id: str) -> None:
        """Remove all questions from a draft"""
        DraftQuestion.objects.filter(
            draft_id=draft_id,
            draft__user_id=user_id
        ).delete()
