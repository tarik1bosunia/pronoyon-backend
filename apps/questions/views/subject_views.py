from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.questions.models import Subject
from apps.questions.serializers import SubjectSerializer, SubjectDetailSerializer
from apps.questions.selectors import SubjectSelectors
from apps.questions.services import SubjectService


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Subject operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        class_id = self.request.query_params.get('class_id')
        search = self.request.query_params.get('search')
        
        if search:
            queryset = SubjectSelectors.search_subjects(
                search_term=search,
                class_id=class_id
            )
        elif class_id:
            queryset = SubjectSelectors.get_subjects_by_class(class_id)
        else:
            queryset = SubjectSelectors.get_subjects_with_chapter_count()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubjectDetailSerializer
        return SubjectSerializer
    
    def create(self, request):
        """Create a new subject"""
        serializer = SubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subject = SubjectService.create_subject(
            user=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            SubjectSerializer(subject).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a subject"""
        subject = Subject.objects.get(id=pk)
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        subject = SubjectService.update_subject(
            subject_id=pk,
            data=serializer.validated_data
        )
        
        return Response(SubjectSerializer(subject).data)
    
    def destroy(self, request, pk=None):
        """Soft delete a subject"""
        SubjectService.delete_subject(subject_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder subjects within a class"""
        class_id = request.data.get('class_id')
        subject_orders = request.data.get('subject_orders', [])
        
        SubjectService.reorder_subjects(
            class_id=class_id,
            subject_orders=subject_orders
        )
        
        return Response({'message': 'Subjects reordered successfully'})
