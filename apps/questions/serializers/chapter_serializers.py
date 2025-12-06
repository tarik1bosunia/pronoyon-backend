from rest_framework import serializers
from apps.questions.models import Chapter


class ChapterSerializer(serializers.ModelSerializer):
    """Serializer for Chapter list"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Chapter
        fields = [
            'id',
            'subject',
            'subject_name',
            'name',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'topic_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChapterDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Chapter with topics"""
    from .topic_serializers import TopicSerializer
    
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = [
            'id',
            'subject',
            'subject_name',
            'name',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'topics',
            'topic_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_topic_count(self, obj):
        return obj.topics.filter(is_active=True).count()
