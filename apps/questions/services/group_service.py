from typing import Dict, Any
from django.db import transaction
from apps.questions.models import Group, Class


class GroupService:
    """Service for Group model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_group(*, user, data: Dict[str, Any]) -> Group:
        """Create a new group"""
        # Validate that the class has_groups flag is True
        class_obj = Class.objects.get(id=data['class_level'])
        if not class_obj.has_groups:
            raise ValueError(f"Class '{class_obj.name}' does not support groups. Set has_groups=True first.")
        
        group = Group.objects.create(
            class_level=class_obj,
            name=data['name'],
            code=data.get('code'),
            group_type=data.get('group_type', Group.GENERAL),
            description=data.get('description', ''),
            order=data.get('order', 0),
            created_by=user
        )
        return group
    
    @staticmethod
    @transaction.atomic
    def update_group(*, group_id: str, data: Dict[str, Any]) -> Group:
        """Update a group"""
        group = Group.objects.get(id=group_id)
        
        if 'name' in data:
            group.name = data['name']
        if 'code' in data:
            group.code = data['code']
        if 'group_type' in data:
            group.group_type = data['group_type']
        if 'description' in data:
            group.description = data['description']
        if 'order' in data:
            group.order = data['order']
        if 'is_active' in data:
            group.is_active = data['is_active']
        
        group.save()
        return group
    
    @staticmethod
    @transaction.atomic
    def delete_group(*, group_id: str) -> None:
        """Soft delete a group"""
        group = Group.objects.get(id=group_id)
        group.is_active = False
        group.save()
    
    @staticmethod
    @transaction.atomic
    def reorder_groups(*, group_orders: list) -> None:
        """Reorder multiple groups within a class
        
        Args:
            group_orders: List of dicts with 'id' and 'order' keys
        """
        for item in group_orders:
            Group.objects.filter(id=item['id']).update(order=item['order'])
    
    @staticmethod
    @transaction.atomic
    def create_default_groups_for_class(*, class_id: str, user) -> list:
        """Create default groups (Science, Arts, Commerce) for a class
        
        Args:
            class_id: ID of the class
            user: User creating the groups
            
        Returns:
            List of created Group objects
        """
        class_obj = Class.objects.get(id=class_id)
        
        # Set has_groups to True if not already
        if not class_obj.has_groups:
            class_obj.has_groups = True
            class_obj.save()
        
        default_groups = [
            {
                'name': 'Science',
                'code': 'SCI',
                'group_type': Group.SCIENCE,
                'order': 1,
                'description': 'Science/Engineering stream'
            },
            {
                'name': 'Arts',
                'code': 'ARTS',
                'group_type': Group.ARTS,
                'order': 2,
                'description': 'Arts/Humanities stream'
            },
            {
                'name': 'Commerce',
                'code': 'COM',
                'group_type': Group.COMMERCE,
                'order': 3,
                'description': 'Commerce/Business Studies stream'
            }
        ]
        
        created_groups = []
        for group_data in default_groups:
            # Check if group already exists
            existing = Group.objects.filter(
                class_level=class_obj,
                name=group_data['name']
            ).first()
            
            if not existing:
                group = Group.objects.create(
                    class_level=class_obj,
                    name=group_data['name'],
                    code=group_data['code'],
                    group_type=group_data['group_type'],
                    description=group_data['description'],
                    order=group_data['order'],
                    created_by=user
                )
                created_groups.append(group)
        
        return created_groups
