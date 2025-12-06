from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.questions.models import Chapter
from apps.questions.serializers import ChapterSerializer, ChapterDetailSerializer
from apps.questions.selectors import ChapterSelectors
from apps.questions.services import ChapterService


class ChapterViewSet(viewsets.ModelViewSet):
    """ViewSet for Chapter operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        subject_id = self.request.query_params.get('subject_id')
        class_id = self.request.query_params.get('class_id')
        search = self.request.query_params.get('search')
        
        if search:
            queryset = ChapterSelectors.search_chapters(
                search_term=search,
                subject_id=subject_id,
                class_id=class_id
            )
        elif subject_id:
            queryset = ChapterSelectors.get_chapters_by_subject(subject_id)
        elif class_id:
            queryset = ChapterSelectors.get_chapters_by_class(class_id)
        else:
            queryset = ChapterSelectors.get_chapters_with_topic_count()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChapterDetailSerializer
        return ChapterSerializer
    
    def create(self, request):
        """Create a new chapter"""
        serializer = ChapterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chapter = ChapterService.create_chapter(
            user=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            ChapterSerializer(chapter).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a chapter"""
        chapter = Chapter.objects.get(id=pk)
        serializer = ChapterSerializer(chapter, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        chapter = ChapterService.update_chapter(
            chapter_id=pk,
            data=serializer.validated_data
        )
        
        return Response(ChapterSerializer(chapter).data)
    
    def destroy(self, request, pk=None):
        """Soft delete a chapter"""
        ChapterService.delete_chapter(chapter_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder chapters within a subject"""
        subject_id = request.data.get('subject_id')
        chapter_orders = request.data.get('chapter_orders', [])
        
        ChapterService.reorder_chapters(
            subject_id=subject_id,
            chapter_orders=chapter_orders
        )
        
        return Response({'message': 'Chapters reordered successfully'})
