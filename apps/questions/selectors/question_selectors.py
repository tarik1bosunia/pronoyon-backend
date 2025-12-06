from django.db.models import Count, Prefetch, Q, QuerySet
from apps.questions.models import Question, MCQOption, CQSubQuestion


class QuestionSelectors:
    """Selectors for Question model"""
    
    @staticmethod
    def get_all_questions(*, is_active: bool = True) -> QuerySet[Question]:
        """Get all questions"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by',
            'verified_by'
        ).prefetch_related('topics', 'topics__chapter')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_question_by_id(question_id: str, *, include_options: bool = True) -> Question:
        """Get question by ID with related data"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by',
            'verified_by'
        ).prefetch_related('topics', 'topics__chapter')
        
        if include_options:
            queryset = queryset.prefetch_related(
                Prefetch('mcq_options', queryset=MCQOption.objects.order_by('order')),
                Prefetch('cq_sub_questions', queryset=CQSubQuestion.objects.order_by('order'))
            )
        
        return queryset.get(id=question_id, is_active=True)
    
    @staticmethod
    def get_questions_by_subject(
        subject_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get questions by subject"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_questions_by_topic(
        topic_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get questions by topic"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(topics__id=topic_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_questions_by_chapter(
        chapter_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get questions by chapter"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(topics__chapter_id=chapter_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.distinct().order_by('-created_at')
    
    @staticmethod
    def get_questions_by_class(
        class_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get questions by class"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(subject__class_level_id=class_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_mcq_questions(
        *,
        subject_id: str = None,
        difficulty: str = None,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get MCQ questions"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related(
            'topics',
            Prefetch('mcq_options', queryset=MCQOption.objects.order_by('order'))
        ).filter(type=Question.MCQ)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_creative_questions(
        *,
        subject_id: str = None,
        difficulty: str = None,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get Creative questions"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related(
            'topics',
            Prefetch('cq_sub_questions', queryset=CQSubQuestion.objects.order_by('order'))
        ).filter(type=Question.CQ)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_questions_by_creator(
        user_id: str,
        *,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get questions created by a user"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(created_by_id=user_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def search_questions(
        search_term: str,
        *,
        question_type: str = None,
        subject_id: str = None,
        difficulty: str = None,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Search questions by text"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(
            Q(question_text__icontains=search_term) | Q(tags__icontains=search_term)
        )
        
        if question_type:
            queryset = queryset.filter(type=question_type)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_verified_questions(
        *,
        subject_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get verified questions"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by',
            'verified_by'
        ).prefetch_related('topics').filter(is_verified=True)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_public_questions(
        *,
        subject_id: str = None,
        is_active: bool = True
    ) -> QuerySet[Question]:
        """Get public questions"""
        queryset = Question.objects.select_related(
            'subject',
            'subject__class_level',
            'created_by'
        ).prefetch_related('topics').filter(is_public=True)
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-created_at')
