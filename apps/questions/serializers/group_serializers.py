from rest_framework import serializers
from apps.questions.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group list"""
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    subject_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Group
        fields = [
            'id',
            'class_level',
            'class_name',
            'name',
            'code',
            'group_type',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'subject_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GroupDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Group with subjects"""
    class_name = serializers.CharField(source='class_level.name', read_only=True)
    subjects = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    
    def get_subjects(self, obj):
        from .subject_serializers import SubjectSerializer
        return SubjectSerializer(obj.subjects.filter(is_active=True), many=True).data
    
    class Meta:
        model = Group
        fields = [
            'id',
            'class_level',
            'class_name',
            'name',
            'code',
            'group_type',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'subjects',
            'subject_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subject_count(self, obj):
        return obj.subjects.filter(is_active=True).count()


class GroupMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Group (for use in nested serializers)"""
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'group_type']
        read_only_fields = ['id']
