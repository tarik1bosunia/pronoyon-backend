from rest_framework import serializers
from apps.questions.models import Question, MCQOption, CQSubQuestion


class MCQOptionSerializer(serializers.ModelSerializer):
    """Serializer for MCQ Options"""
    
    class Meta:
        model = MCQOption
        fields = [
            'id',
            'option_label',
            'option_text',
            'option_text_html',
            'is_correct',
            'order',
            'combined_option_indices'
        ]
        read_only_fields = ['id']


class CQSubQuestionSerializer(serializers.ModelSerializer):
    """Serializer for CQ Sub-questions"""
    
    class Meta:
        model = CQSubQuestion
        fields = [
            'id',
            'label',
            'sub_question_text',
            'sub_question_text_html',
            'marks',
            'answer',
            'answer_html',
            'order'
        ]
        read_only_fields = ['id']


class QuestionListSerializer(serializers.ModelSerializer):
    """Serializer for Question list"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='subject.class_level.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.email', read_only=True)
    topic_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id',
            'type',
            'mcq_subtype',
            'question_text',
            'marks',
            'difficulty',
            'subject',
            'subject_name',
            'class_name',
            'topic_names',
            'tags',
            'is_public',
            'is_active',
            'is_verified',
            'creator_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_topic_names(self, obj):
        return [topic.name for topic in obj.topics.all()]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Question"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='subject.class_level.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.email', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.email', read_only=True)
    mcq_options = MCQOptionSerializer(many=True, read_only=True)
    cq_sub_questions = CQSubQuestionSerializer(many=True, read_only=True)
    topics = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id',
            'type',
            'mcq_subtype',
            'question_text',
            'question_text_html',
            'marks',
            'difficulty',
            'subject',
            'subject_name',
            'class_name',
            'topics',
            'tags',
            'solution',
            'solution_html',
            'hints',
            'mcq_options',
            'cq_sub_questions',
            'is_public',
            'is_active',
            'is_verified',
            'creator_name',
            'verified_by_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_topics(self, obj):
        return [{'id': str(topic.id), 'name': topic.name} for topic in obj.topics.all()]


class MCQQuestionCreateSerializer(serializers.Serializer):
    """Serializer for creating MCQ questions"""
    mcq_subtype = serializers.ChoiceField(choices=Question.MCQ_SUBTYPE_CHOICES, default=Question.SIMPLE)
    question_text = serializers.CharField()
    marks = serializers.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    difficulty = serializers.ChoiceField(choices=Question.DIFFICULTY_CHOICES, default=Question.MEDIUM)
    subject_id = serializers.UUIDField()
    topic_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    solution = serializers.CharField(required=False, allow_blank=True, default='')
    hints = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    is_public = serializers.BooleanField(default=True)
    options = serializers.ListField(child=serializers.DictField(), min_length=2)


class CQQuestionCreateSerializer(serializers.Serializer):
    """Serializer for creating Creative questions"""
    question_text = serializers.CharField()
    marks = serializers.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    difficulty = serializers.ChoiceField(choices=Question.DIFFICULTY_CHOICES, default=Question.MEDIUM)
    subject_id = serializers.UUIDField()
    topic_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    solution = serializers.CharField(required=False, allow_blank=True, default='')
    hints = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    is_public = serializers.BooleanField(default=True)
    sub_questions = serializers.ListField(child=serializers.DictField(), min_length=1)
