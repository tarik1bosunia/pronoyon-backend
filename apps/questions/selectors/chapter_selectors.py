from django.db.models import Count, Prefetch, Q, QuerySet
from apps.questions.models import Chapter, Topic


class ChapterSelectors:
    """Selectors for Chapter model"""
    
    @staticmethod
    def get_all_chapters(*, is_active: bool = True) -> QuerySet[Chapter]:
        """Get all chapters"""
        queryset = Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('subject__class_level__order', 'subject__order', 'order', 'name')
    
    @staticmethod
    def get_chapter_by_id(chapter_id: str) -> Chapter:
        """Get chapter by ID"""
        return Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        ).get(id=chapter_id, is_active=True)
    
    @staticmethod
    def get_chapters_by_subject(
        subject_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Chapter]:
        """Get all chapters for a specific subject"""
        queryset = Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        ).filter(subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def get_chapters_by_class(
        class_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Chapter]:
        """Get all chapters for a specific class"""
        queryset = Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        ).filter(subject__class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('subject__order', 'order', 'name')
    
    @staticmethod
    def get_chapters_with_topics(
        *,
        subject_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Chapter]:
        """Get chapters with their topics"""
        queryset = Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        ).prefetch_related(
            Prefetch(
                'topics',
                queryset=Topic.objects.filter(is_active=True) if is_active else Topic.objects.all()
            )
        )
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('subject__class_level__order', 'subject__order', 'order', 'name')
    
    @staticmethod
    def get_chapters_with_topic_count(
        *,
        subject_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Chapter]:
        """Get chapters with topic count"""
        queryset = Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        ).annotate(
            topic_count=Count('topics', filter=Q(topics__is_active=True))
        )
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('subject__class_level__order', 'subject__order', 'order', 'name')
    
    @staticmethod
    def search_chapters(
        search_term: str,
        *,
        subject_id: str = None,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Chapter]:
        """Search chapters by name"""
        queryset = Chapter.objects.select_related(
            'subject',
            'subject__class_level'
        ).filter(name__icontains=search_term)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if class_id:
            queryset = queryset.filter(subject__class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('subject__class_level__order', 'subject__order', 'order', 'name')
