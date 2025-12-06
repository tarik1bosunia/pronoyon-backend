from rest_framework import serializers
from apps.questions.models import Class


class ClassSerializer(serializers.ModelSerializer):
    """Serializer for Class list"""
    subject_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id',
            'name',
            'code',
            'description',
            'order',
            'is_active',
            'created_at',
            'updated_at',
            'subject_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Class with subjects"""
    from .subject_serializers import SubjectSerializer
    
    subjects = SubjectSerializer(many=True, read_only=True)
    subject_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id',
            'name',
            'code',
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
