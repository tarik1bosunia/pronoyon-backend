from typing import Dict, Any
from django.db import transaction
from apps.questions.models import Topic


class TopicService:
    """Service for Topic model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_topic(*, user, data: Dict[str, Any]) -> Topic:
        """Create a new topic"""
        # Handle both 'chapter' and 'chapter_id' keys
        # validated_data may contain the object itself or the ID
        chapter = data.get('chapter_id') or data.get('chapter')
        chapter_id = chapter.id if hasattr(chapter, 'id') else chapter
        topic = Topic.objects.create(
            chapter_id=chapter_id,
            name=data['name'],
            description=data.get('description', ''),
            order=data.get('order', 0),
            created_by=user
        )
        return topic
    
    @staticmethod
    @transaction.atomic
    def update_topic(*, topic_id: str, data: Dict[str, Any]) -> Topic:
        """Update a topic"""
        topic = Topic.objects.get(id=topic_id)
        
        # Handle both 'chapter' and 'chapter_id' keys
        if 'chapter_id' in data or 'chapter' in data:
            chapter = data.get('chapter_id') or data.get('chapter')
            topic.chapter_id = chapter.id if hasattr(chapter, 'id') else chapter
        if 'name' in data:
            topic.name = data['name']
        if 'description' in data:
            topic.description = data['description']
        if 'order' in data:
            topic.order = data['order']
        if 'is_active' in data:
            topic.is_active = data['is_active']
        
        topic.save()
        return topic
    
    @staticmethod
    @transaction.atomic
    def delete_topic(*, topic_id: str) -> None:
        """Soft delete a topic"""
        topic = Topic.objects.get(id=topic_id)
        topic.is_active = False
        topic.save()
    
    @staticmethod
    @transaction.atomic
    def reorder_topics(*, chapter_id: str, topic_orders: list) -> None:
        """Reorder topics within a chapter
        
        Args:
            chapter_id: The chapter ID
            topic_orders: List of dicts with 'id' and 'order' keys
        """
        for item in topic_orders:
            Topic.objects.filter(
                id=item['id'],
                chapter_id=chapter_id
            ).update(order=item['order'])
