from rest_framework import serializers
from apps.questions.models import Topic


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic list"""
    chapter_name = serializers.CharField(source='chapter.name', read_only=True)
    subject_name = serializers.CharField(source='chapter.subject.name', read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Topic
        fields = [
            'id',
            'chapter',
            'chapter_name',
            'subject_name',
            'name',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'question_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TopicDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Topic"""
    chapter_name = serializers.CharField(source='chapter.name', read_only=True)
    subject_name = serializers.CharField(source='chapter.subject.name', read_only=True)
    class_name = serializers.CharField(source='chapter.subject.class_level.name', read_only=True)
    
    class Meta:
        model = Topic
        fields = [
            'id',
            'chapter',
            'chapter_name',
            'subject_name',
            'class_name',
            'name',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
