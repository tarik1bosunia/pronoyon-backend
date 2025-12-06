from rest_framework import serializers
from apps.questions.models import UserDraft, DraftQuestion
from .question_serializers import QuestionListSerializer


class UserDraftSerializer(serializers.ModelSerializer):
    """Serializer for UserDraft list"""
    question_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = UserDraft
        fields = [
            'id',
            'title',
            'description',
            'is_favorite',
            'question_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'question_count']


class DraftQuestionSerializer(serializers.ModelSerializer):
    """Serializer for DraftQuestion"""
    question = QuestionListSerializer(read_only=True)
    
    class Meta:
        model = DraftQuestion
        fields = [
            'id',
            'question',
            'order',
            'notes',
            'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class UserDraftDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for UserDraft with questions"""
    draft_questions = DraftQuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDraft
        fields = [
            'id',
            'title',
            'description',
            'is_favorite',
            'draft_questions',
            'question_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_question_count(self, obj):
        return obj.draft_questions.count()
