from typing import Dict, Any
from django.db import transaction
from apps.questions.models import Class


class ClassService:
    """Service for Class model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_class(*, user, data: Dict[str, Any]) -> Class:
        """Create a new class"""
        class_obj = Class.objects.create(
            name=data['name'],
            code=data.get('code'),
            description=data.get('description', ''),
            order=data.get('order', 0),
            created_by=user
        )
        return class_obj
    
    @staticmethod
    @transaction.atomic
    def update_class(*, class_id: str, data: Dict[str, Any]) -> Class:
        """Update a class"""
        class_obj = Class.objects.get(id=class_id)
        
        if 'name' in data:
            class_obj.name = data['name']
        if 'code' in data:
            class_obj.code = data['code']
        if 'description' in data:
            class_obj.description = data['description']
        if 'order' in data:
            class_obj.order = data['order']
        if 'is_active' in data:
            class_obj.is_active = data['is_active']
        
        class_obj.save()
        return class_obj
    
    @staticmethod
    @transaction.atomic
    def delete_class(*, class_id: str) -> None:
        """Soft delete a class"""
        class_obj = Class.objects.get(id=class_id)
        class_obj.is_active = False
        class_obj.save()
    
    @staticmethod
    @transaction.atomic
    def reorder_classes(*, class_orders: list) -> None:
        """Reorder multiple classes
        
        Args:
            class_orders: List of dicts with 'id' and 'order' keys
        """
        for item in class_orders:
            Class.objects.filter(id=item['id']).update(order=item['order'])
