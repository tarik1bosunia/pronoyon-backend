from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.questions.models import Question
from apps.questions.serializers import (
    QuestionListSerializer,
    QuestionDetailSerializer,
    MCQQuestionCreateSerializer,
    CQQuestionCreateSerializer
)
from apps.questions.selectors import QuestionSelectors
from apps.questions.services import QuestionService


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for Question operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        subject_id = self.request.query_params.get('subject_id')
        topic_id = self.request.query_params.get('topic_id')
        chapter_id = self.request.query_params.get('chapter_id')
        class_id = self.request.query_params.get('class_id')
        question_type = self.request.query_params.get('type')
        difficulty = self.request.query_params.get('difficulty')
        search = self.request.query_params.get('search')
        is_verified = self.request.query_params.get('is_verified')
        
        if search:
            queryset = QuestionSelectors.search_questions(
                search_term=search,
                question_type=question_type,
                subject_id=subject_id,
                difficulty=difficulty
            )
        elif topic_id:
            queryset = QuestionSelectors.get_questions_by_topic(topic_id)
        elif chapter_id:
            queryset = QuestionSelectors.get_questions_by_chapter(chapter_id)
        elif subject_id:
            queryset = QuestionSelectors.get_questions_by_subject(subject_id)
        elif class_id:
            queryset = QuestionSelectors.get_questions_by_class(class_id)
        elif is_verified == 'true':
            queryset = QuestionSelectors.get_verified_questions()
        else:
            queryset = QuestionSelectors.get_all_questions()
        
        # Filter by type
        if question_type:
            queryset = queryset.filter(type=question_type)
        
        # Filter by difficulty
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuestionDetailSerializer
        return QuestionListSerializer
    
    def create(self, request):
        """Create a new question"""
        question_type = request.data.get('type')
        
        if question_type == Question.MCQ:
            serializer = MCQQuestionCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            question = QuestionService.create_mcq_question(
                user=request.user,
                data=serializer.validated_data
            )
        elif question_type == Question.CQ:
            serializer = CQQuestionCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            question = QuestionService.create_creative_question(
                user=request.user,
                data=serializer.validated_data
            )
        else:
            return Response(
                {'error': 'Invalid question type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            QuestionDetailSerializer(question).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a question"""
        question = QuestionService.update_question(
            question_id=pk,
            data=request.data
        )
        
        return Response(QuestionDetailSerializer(question).data)
    
    def destroy(self, request, pk=None):
        """Soft delete a question"""
        QuestionService.delete_question(question_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a question"""
        question = QuestionService.verify_question(
            question_id=pk,
            user=request.user
        )
        return Response(QuestionDetailSerializer(question).data)
    
    @action(detail=True, methods=['post'])
    def unverify(self, request, pk=None):
        """Unverify a question"""
        question = QuestionService.unverify_question(question_id=pk)
        return Response(QuestionDetailSerializer(question).data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a question"""
        question = QuestionService.duplicate_question(
            question_id=pk,
            user=request.user
        )
        return Response(
            QuestionDetailSerializer(question).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def my_questions(self, request):
        """Get questions created by the current user"""
        queryset = QuestionSelectors.get_questions_by_creator(request.user.id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QuestionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = QuestionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mcq(self, request):
        """Get MCQ questions"""
        subject_id = request.query_params.get('subject_id')
        difficulty = request.query_params.get('difficulty')
        
        queryset = QuestionSelectors.get_mcq_questions(
            subject_id=subject_id,
            difficulty=difficulty
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QuestionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = QuestionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def creative(self, request):
        """Get Creative questions"""
        subject_id = request.query_params.get('subject_id')
        difficulty = request.query_params.get('difficulty')
        
        queryset = QuestionSelectors.get_creative_questions(
            subject_id=subject_id,
            difficulty=difficulty
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QuestionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = QuestionListSerializer(queryset, many=True)
        return Response(serializer.data)
