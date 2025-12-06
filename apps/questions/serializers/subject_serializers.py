from rest_framework import serializers
from apps.questions.models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject list"""
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    chapter_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'class_level',
            'class_name',
            'name',
            'code',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'chapter_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Subject with chapters"""
    from .chapter_serializers import ChapterSerializer
    
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    chapter_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'class_level',
            'class_name',
            'name',
            'code',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'chapters',
            'chapter_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_chapter_count(self, obj):
        return obj.chapters.filter(is_active=True).count()
