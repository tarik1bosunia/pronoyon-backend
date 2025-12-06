from typing import Dict, Any
from django.db import transaction
from apps.questions.models import Subject


class SubjectService:
    """Service for Subject model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_subject(*, user, data: Dict[str, Any]) -> Subject:
        """Create a new subject"""
        # Handle both 'class_level' and 'class_level_id' keys
        # validated_data may contain the object itself or the ID
        class_level = data.get('class_level_id') or data.get('class_level')
        class_level_id = class_level.id if hasattr(class_level, 'id') else class_level
        
        # Handle group
        group = data.get('group_id') or data.get('group')
        group_id = None
        if group:
            group_id = group.id if hasattr(group, 'id') else group
        
        subject = Subject.objects.create(
            class_level_id=class_level_id,
            group_id=group_id,
            name=data['name'],
            code=data.get('code'),
            description=data.get('description', ''),
            order=data.get('order', 0),
            created_by=user
        )
        return subject
    
    @staticmethod
    @transaction.atomic
    def update_subject(*, subject_id: str, data: Dict[str, Any]) -> Subject:
        """Update a subject"""
        subject = Subject.objects.get(id=subject_id)
        
        # Handle both 'class_level' and 'class_level_id' keys
        if 'class_level_id' in data or 'class_level' in data:
            class_level = data.get('class_level_id') or data.get('class_level')
            subject.class_level_id = class_level.id if hasattr(class_level, 'id') else class_level
        
        # Handle group
        if 'group_id' in data or 'group' in data:
            group = data.get('group_id') or data.get('group')
            subject.group_id = group.id if (group and hasattr(group, 'id')) else group
        
        if 'name' in data:
            subject.name = data['name']
        if 'code' in data:
            subject.code = data['code']
        if 'description' in data:
            subject.description = data['description']
        if 'order' in data:
            subject.order = data['order']
        if 'is_active' in data:
            subject.is_active = data['is_active']
        
        subject.save()
        return subject
    
    @staticmethod
    @transaction.atomic
    def delete_subject(*, subject_id: str) -> None:
        """Soft delete a subject"""
        subject = Subject.objects.get(id=subject_id)
        subject.is_active = False
        subject.save()
    
    @staticmethod
    @transaction.atomic
    def reorder_subjects(*, class_id: str, subject_orders: list) -> None:
        """Reorder subjects within a class
        
        Args:
            class_id: The class ID
            subject_orders: List of dicts with 'id' and 'order' keys
        """
        for item in subject_orders:
            Subject.objects.filter(
                id=item['id'],
                class_level_id=class_id
            ).update(order=item['order'])
