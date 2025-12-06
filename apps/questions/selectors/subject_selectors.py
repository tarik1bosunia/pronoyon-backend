from django.db.models import Count, Prefetch, Q, QuerySet
from apps.questions.models import Subject, Chapter


class SubjectSelectors:
    """Selectors for Subject model"""
    
    @staticmethod
    def get_all_subjects(*, is_active: bool = True) -> QuerySet[Subject]:
        """Get all subjects"""
        queryset = Subject.objects.select_related('class_level')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def get_subject_by_id(subject_id: str) -> Subject:
        """Get subject by ID"""
        return Subject.objects.select_related('class_level').get(
            id=subject_id, is_active=True
        )
    
    @staticmethod
    def get_subjects_by_class(
        class_id: str, 
        *, 
        is_active: bool = True
    ) -> QuerySet[Subject]:
        """Get all subjects for a specific class"""
        queryset = Subject.objects.select_related('class_level').filter(
            class_level_id=class_id
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def get_subjects_with_chapters(
        *, 
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Subject]:
        """Get subjects with their chapters"""
        queryset = Subject.objects.select_related('class_level').prefetch_related(
            Prefetch(
                'chapters',
                queryset=Chapter.objects.filter(is_active=True) if is_active else Chapter.objects.all()
            )
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def get_subjects_with_chapter_count(
        *,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Subject]:
        """Get subjects with chapter count"""
        queryset = Subject.objects.select_related('class_level').annotate(
            chapter_count=Count('chapters', filter=Q(chapters__is_active=True))
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
    
    @staticmethod
    def search_subjects(
        search_term: str,
        *,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Subject]:
        """Search subjects by name or code"""
        queryset = Subject.objects.select_related('class_level').filter(
            Q(name__icontains=search_term) | Q(code__icontains=search_term)
        )
        
        if class_id:
            queryset = queryset.filter(class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('class_level__order', 'order', 'name')
