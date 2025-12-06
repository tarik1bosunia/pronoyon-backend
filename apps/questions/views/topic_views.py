from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.questions.models import Topic
from apps.questions.serializers import TopicSerializer, TopicDetailSerializer
from apps.questions.selectors import TopicSelectors
from apps.questions.services import TopicService


class TopicViewSet(viewsets.ModelViewSet):
    """ViewSet for Topic operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        chapter_id = self.request.query_params.get('chapter_id')
        subject_id = self.request.query_params.get('subject_id')
        class_id = self.request.query_params.get('class_id')
        search = self.request.query_params.get('search')
        
        if search:
            queryset = TopicSelectors.search_topics(
                search_term=search,
                chapter_id=chapter_id,
                subject_id=subject_id,
                class_id=class_id
            )
        elif chapter_id:
            queryset = TopicSelectors.get_topics_by_chapter(chapter_id)
        elif subject_id:
            queryset = TopicSelectors.get_topics_by_subject(subject_id)
        elif class_id:
            queryset = TopicSelectors.get_topics_by_class(class_id)
        else:
            queryset = TopicSelectors.get_topics_with_question_count()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TopicDetailSerializer
        return TopicSerializer
    
    def create(self, request):
        """Create a new topic"""
        serializer = TopicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        topic = TopicService.create_topic(
            user=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            TopicSerializer(topic).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a topic"""
        topic = Topic.objects.get(id=pk)
        serializer = TopicSerializer(topic, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        topic = TopicService.update_topic(
            topic_id=pk,
            data=serializer.validated_data
        )
        
        return Response(TopicSerializer(topic).data)
    
    def destroy(self, request, pk=None):
        """Soft delete a topic"""
        TopicService.delete_topic(topic_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder topics within a chapter"""
        chapter_id = request.data.get('chapter_id')
        topic_orders = request.data.get('topic_orders', [])
        
        TopicService.reorder_topics(
            chapter_id=chapter_id,
            topic_orders=topic_orders
        )
        
        return Response({'message': 'Topics reordered successfully'})
