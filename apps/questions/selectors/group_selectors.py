from django.db.models import Count, Prefetch, Q, QuerySet
from apps.questions.models import Group, Subject


class GroupSelectors:
    """Selectors for Group model"""
    
    @staticmethod
    def get_all_groups(*, is_active: bool = True) -> QuerySet[Group]:
        """Get all groups"""
        queryset = Group.objects.select_related('class_level')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def get_group_by_id(group_id: str) -> Group:
        """Get group by ID"""
        return Group.objects.select_related('class_level').get(
            id=group_id, is_active=True
        )
    
    @staticmethod
    def get_group_by_code(code: str, class_id: str = None) -> Group:
        """Get group by code"""
        queryset = Group.objects.filter(code=code, is_active=True)
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        return queryset.get()
    
    @staticmethod
    def get_groups_by_class(
        class_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Group]:
        """Get all groups for a specific class"""
        queryset = Group.objects.select_related('class_level').filter(
            class_level_id=class_id
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def get_groups_by_type(
        group_type: str,
        *,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Group]:
        """Get groups by type (science, arts, commerce)"""
        queryset = Group.objects.select_related('class_level').filter(
            group_type=group_type
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def get_groups_with_subjects(
        *,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Group]:
        """Get groups with their subjects"""
        queryset = Group.objects.select_related('class_level').prefetch_related(
            Prefetch(
                'subjects',
                queryset=Subject.objects.filter(is_active=True) if is_active else Subject.objects.all()
            )
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def get_groups_with_subject_count(
        *,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Group]:
        """Get groups with subject count"""
        queryset = Group.objects.select_related('class_level').annotate(
            subject_count=Count('subjects', filter=Q(subjects__is_active=True))
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def search_groups(
        search_term: str,
        *,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Group]:
        """Search groups by name or code"""
        queryset = Group.objects.select_related('class_level').filter(
            Q(name__icontains=search_term) | Q(code__icontains=search_term)
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def check_class_has_groups(class_id: str) -> bool:
        """Check if a class has any groups defined"""
        from apps.questions.models import Class
        
        try:
            class_obj = Class.objects.get(id=class_id, is_active=True)
            return class_obj.has_groups and class_obj.groups.filter(is_active=True).exists()
        except Class.DoesNotExist:
            return False
