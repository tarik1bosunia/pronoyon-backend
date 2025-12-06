from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.questions.models import Class
from apps.questions.serializers import ClassSerializer, ClassDetailSerializer
from apps.questions.selectors import ClassSelectors
from apps.questions.services import ClassService


class ClassViewSet(viewsets.ModelViewSet):
    """ViewSet for Class operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ClassSelectors.get_classes_with_subject_count()
        
        # Filter by search term
        search = self.request.query_params.get('search')
        if search:
            queryset = ClassSelectors.search_classes(search)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassDetailSerializer
        return ClassSerializer
    
    def create(self, request):
        """Create a new class"""
        serializer = ClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        class_obj = ClassService.create_class(
            user=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            ClassSerializer(class_obj).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """Update a class"""
        serializer = ClassSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        class_obj = ClassService.update_class(
            class_id=pk,
            data=serializer.validated_data
        )
        
        return Response(ClassSerializer(class_obj).data)
    
    def destroy(self, request, pk=None):
        """Soft delete a class"""
        ClassService.delete_class(class_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder classes"""
        class_orders = request.data.get('class_orders', [])
        ClassService.reorder_classes(class_orders=class_orders)
        return Response({'message': 'Classes reordered successfully'})
    
    @action(detail=True, methods=['get'])
    def with_subjects(self, request, pk=None):
        """Get class with subjects"""
        class_obj = ClassSelectors.get_class_by_id(pk)
        serializer = ClassDetailSerializer(class_obj)
        return Response(serializer.data)
