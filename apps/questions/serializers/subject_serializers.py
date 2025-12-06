from rest_framework import serializers
from apps.questions.models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject list"""
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    group_info = serializers.SerializerMethodField()
    chapter_count = serializers.IntegerField(read_only=True)
    
    def get_group_info(self, obj):
        if obj.group:
            from .group_serializers import GroupMinimalSerializer
            return GroupMinimalSerializer(obj.group).data
        return None
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'class_level',
            'class_name',
            'group',
            'group_info',
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
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    group_info = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()
    chapter_count = serializers.SerializerMethodField()
    
    def get_group_info(self, obj):
        if obj.group:
            from .group_serializers import GroupMinimalSerializer
            return GroupMinimalSerializer(obj.group).data
        return None
    
    def get_chapters(self, obj):
        from .chapter_serializers import ChapterSerializer
        return ChapterSerializer(obj.chapters.filter(is_active=True), many=True).data
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'class_level',
            'class_name',
            'group',
            'group_info',
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
