from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.questions.models import UserDraft
from apps.questions.serializers import (
    UserDraftSerializer,
    UserDraftDetailSerializer
)
from apps.questions.selectors import DraftSelectors
from apps.questions.services import DraftService


class UserDraftViewSet(viewsets.ModelViewSet):
    """ViewSet for UserDraft operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        search = self.request.query_params.get('search')
        favorites_only = self.request.query_params.get('favorites')
        
        if search:
            queryset = DraftSelectors.search_user_drafts(
                user_id=self.request.user.id,
                search_term=search
            )
        elif favorites_only == 'true':
            queryset = DraftSelectors.get_favorite_drafts(
                user_id=self.request.user.id
            )
        else:
            queryset = DraftSelectors.get_user_drafts(
                user_id=self.request.user.id
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDraftDetailSerializer
        return UserDraftSerializer
    
    def retrieve(self, request, pk=None):
        """Get draft with questions"""
        draft = DraftSelectors.get_draft_with_questions(
            draft_id=pk,
            user_id=request.user.id
        )
        serializer = UserDraftDetailSerializer(draft)
        return Response(serializer.data)
    
    def create(self, request):
        """Create a new draft"""
        serializer = UserDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        draft = DraftService.create_draft(
            user=request.user,
            data=serializer.validated_data
        )
        
        return Response(
            UserDraftSerializer(draft).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """Update a draft"""
        serializer = UserDraftSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        draft = DraftService.update_draft(
            draft_id=pk,
            user_id=request.user.id,
            data=serializer.validated_data
        )
        
        return Response(UserDraftSerializer(draft).data)
    
    def destroy(self, request, pk=None):
        """Delete a draft"""
        DraftService.delete_draft(
            draft_id=pk,
            user_id=request.user.id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        """Add a question to draft"""
        question_id = request.data.get('question_id')
        notes = request.data.get('notes', '')
        
        draft_question = DraftService.add_question_to_draft(
            draft_id=pk,
            user_id=request.user.id,
            question_id=question_id,
            notes=notes
        )
        
        return Response({'message': 'Question added to draft'})
    
    @action(detail=True, methods=['post'])
    def add_multiple_questions(self, request, pk=None):
        """Add multiple questions to draft"""
        question_ids = request.data.get('question_ids', [])
        
        DraftService.add_multiple_questions_to_draft(
            draft_id=pk,
            user_id=request.user.id,
            question_ids=question_ids
        )
        
        return Response({'message': f'{len(question_ids)} questions added to draft'})
    
    @action(detail=True, methods=['post'])
    def remove_question(self, request, pk=None):
        """Remove a question from draft"""
        question_id = request.data.get('question_id')
        
        DraftService.remove_question_from_draft(
            draft_id=pk,
            user_id=request.user.id,
            question_id=question_id
        )
        
        return Response({'message': 'Question removed from draft'})
    
    @action(detail=True, methods=['post'])
    def update_question_notes(self, request, pk=None):
        """Update notes for a question in draft"""
        question_id = request.data.get('question_id')
        notes = request.data.get('notes', '')
        
        DraftService.update_draft_question_notes(
            draft_id=pk,
            user_id=request.user.id,
            question_id=question_id,
            notes=notes
        )
        
        return Response({'message': 'Notes updated'})
    
    @action(detail=True, methods=['post'])
    def reorder_questions(self, request, pk=None):
        """Reorder questions in draft"""
        question_orders = request.data.get('question_orders', [])
        
        DraftService.reorder_draft_questions(
            draft_id=pk,
            user_id=request.user.id,
            question_orders=question_orders
        )
        
        return Response({'message': 'Questions reordered'})
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status"""
        draft = DraftService.toggle_draft_favorite(
            draft_id=pk,
            user_id=request.user.id
        )
        
        return Response(UserDraftSerializer(draft).data)
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Remove all questions from draft"""
        DraftService.clear_draft(
            draft_id=pk,
            user_id=request.user.id
        )
        
        return Response({'message': 'Draft cleared'})
