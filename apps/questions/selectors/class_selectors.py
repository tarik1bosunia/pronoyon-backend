from django.db.models import Count, Prefetch, Q, QuerySet
from apps.questions.models import Class


class ClassSelectors:
    """Selectors for Class model"""
    
    @staticmethod
    def get_all_classes(*, is_active: bool = True) -> QuerySet[Class]:
        """Get all classes"""
        queryset = Class.objects.all()
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def get_class_by_id(class_id: str) -> Class:
        """Get class by ID"""
        return Class.objects.get(id=class_id, is_active=True)
    
    @staticmethod
    def get_class_by_code(code: str) -> Class:
        """Get class by code"""
        return Class.objects.get(code=code, is_active=True)
    
    @staticmethod
    def get_classes_with_subjects(*, is_active: bool = True) -> QuerySet[Class]:
        """Get classes with their subjects"""
        queryset = Class.objects.prefetch_related(
            Prefetch(
                'subjects',
                queryset=Class.objects.filter(is_active=True) if is_active else Class.objects.all()
            )
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def get_classes_with_subject_count(*, is_active: bool = True) -> QuerySet[Class]:
        """Get classes with subject count"""
        queryset = Class.objects.annotate(
            subject_count=Count('subjects', filter=Q(subjects__is_active=True))
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def search_classes(search_term: str, *, is_active: bool = True) -> QuerySet[Class]:
        """Search classes by name or code"""
        queryset = Class.objects.filter(
            Q(name__icontains=search_term) | Q(code__icontains=search_term)
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
