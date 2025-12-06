from django.db.models import Count, Q, QuerySet
from apps.questions.models import Topic


class TopicSelectors:
    """Selectors for Topic model"""
    
    @staticmethod
    def get_all_topics(*, is_active: bool = True) -> QuerySet[Topic]:
        """Get all topics"""
        queryset = Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by(
            'chapter__subject__class_level__order',
            'chapter__subject__order',
            'chapter__order',
            'order',
            'name'
        )
    
    @staticmethod
    def get_topic_by_id(topic_id: str) -> Topic:
        """Get topic by ID"""
        return Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        ).get(id=topic_id, is_active=True)
    
    @staticmethod
    def get_topics_by_chapter(
        chapter_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Topic]:
        """Get all topics for a specific chapter"""
        queryset = Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        ).filter(chapter_id=chapter_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('order', 'name')
    
    @staticmethod
    def get_topics_by_subject(
        subject_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Topic]:
        """Get all topics for a specific subject"""
        queryset = Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        ).filter(chapter__subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('chapter__order', 'order', 'name')
    
    @staticmethod
    def get_topics_by_class(
        class_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Topic]:
        """Get all topics for a specific class"""
        queryset = Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        ).filter(chapter__subject__class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('chapter__subject__order', 'chapter__order', 'order', 'name')
    
    @staticmethod
    def get_topics_with_question_count(
        *,
        chapter_id: str = None,
        subject_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Topic]:
        """Get topics with question count"""
        queryset = Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        ).annotate(
            question_count=Count('questions', filter=Q(questions__is_active=True))
        )
        
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        
        if subject_id:
            queryset = queryset.filter(chapter__subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by(
            'chapter__subject__class_level__order',
            'chapter__subject__order',
            'chapter__order',
            'order',
            'name'
        )
    
    @staticmethod
    def search_topics(
        search_term: str,
        *,
        chapter_id: str = None,
        subject_id: str = None,
        class_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Topic]:
        """Search topics by name"""
        queryset = Topic.objects.select_related(
            'chapter',
            'chapter__subject',
            'chapter__subject__class_level'
        ).filter(name__icontains=search_term)
        
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        
        if subject_id:
            queryset = queryset.filter(chapter__subject_id=subject_id)
        
        if class_id:
            queryset = queryset.filter(chapter__subject__class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by(
            'chapter__subject__class_level__order',
            'chapter__subject__order',
            'chapter__order',
            'order',
            'name'
        )
