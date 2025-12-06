from typing import Dict, Any
from django.db import transaction
from apps.questions.models import Chapter


class ChapterService:
    """Service for Chapter model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_chapter(*, user, data: Dict[str, Any]) -> Chapter:
        """Create a new chapter"""
        # Handle both 'subject' and 'subject_id' keys
        # validated_data may contain the object itself or the ID
        subject = data.get('subject_id') or data.get('subject')
        subject_id = subject.id if hasattr(subject, 'id') else subject
        chapter = Chapter.objects.create(
            subject_id=subject_id,
            name=data['name'],
            description=data.get('description', ''),
            order=data.get('order', 0),
            created_by=user
        )
        return chapter
    
    @staticmethod
    @transaction.atomic
    def update_chapter(*, chapter_id: str, data: Dict[str, Any]) -> Chapter:
        """Update a chapter"""
        chapter = Chapter.objects.get(id=chapter_id)
        
        # Handle both 'subject' and 'subject_id' keys
        if 'subject_id' in data or 'subject' in data:
            subject = data.get('subject_id') or data.get('subject')
            chapter.subject_id = subject.id if hasattr(subject, 'id') else subject
        if 'name' in data:
            chapter.name = data['name']
        if 'description' in data:
            chapter.description = data['description']
        if 'order' in data:
            chapter.order = data['order']
        if 'is_active' in data:
            chapter.is_active = data['is_active']
        
        chapter.save()
        return chapter
    
    @staticmethod
    @transaction.atomic
    def delete_chapter(*, chapter_id: str) -> None:
        """Soft delete a chapter"""
        chapter = Chapter.objects.get(id=chapter_id)
        chapter.is_active = False
        chapter.save()
    
    @staticmethod
    @transaction.atomic
    def reorder_chapters(*, subject_id: str, chapter_orders: list) -> None:
        """Reorder chapters within a subject
        
        Args:
            subject_id: The subject ID
            chapter_orders: List of dicts with 'id' and 'order' keys
        """
        for item in chapter_orders:
            Chapter.objects.filter(
                id=item['id'],
                subject_id=subject_id
            ).update(order=item['order'])
