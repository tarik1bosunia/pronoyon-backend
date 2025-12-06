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


class FrontendMCQOptionSerializer(serializers.Serializer):
    """Frontend compatible MCQ option serializer"""
    id = serializers.CharField()
    text = serializers.CharField(source='option_text')
    isCorrect = serializers.BooleanField(source='is_correct')


class FrontendCQSubQuestionSerializer(serializers.Serializer):
    """Frontend compatible CQ sub-question serializer"""
    id = serializers.CharField()
    label = serializers.CharField()
    text = serializers.CharField(source='sub_question_text')
    marks = serializers.DecimalField(max_digits=5, decimal_places=2)


class FrontendQuestionSerializer(serializers.ModelSerializer):
    """Frontend compatible question serializer matching the React Question type"""
    type = serializers.SerializerMethodField()
    text = serializers.CharField(source='question_text')
    stem = serializers.SerializerMethodField()
    romanStatements = serializers.SerializerMethodField()
    footer = serializers.SerializerMethodField()
    board = serializers.CharField(source='subject.class_level.name', default='')
    year = serializers.SerializerMethodField()
    subject = serializers.CharField(source='subject.name', default='')
    chapter = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()
    schoolYear = serializers.SerializerMethodField()
    specialTags = serializers.ListField(source='tags', default=list)
    options = serializers.SerializerMethodField()
    subQuestions = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id',
            'type',
            'text',
            'stem',
            'romanStatements',
            'footer',
            'marks',
            'board',
            'year',
            'subject',
            'chapter',
            'topic',
            'school',
            'schoolYear',
            'specialTags',
            'options',
            'subQuestions'
        ]
    
    def get_type(self, obj):
        return obj.type.lower()
    
    def get_stem(self, obj):
        """Extract stem for combined MCQ"""
        if obj.type == Question.MCQ and obj.mcq_subtype == Question.COMBINED:
            lines = obj.question_text.split('\n')
            if lines:
                return lines[0].strip()
        return None
    
    def get_romanStatements(self, obj):
        """Extract roman numeral statements for combined MCQ"""
        if obj.type == Question.MCQ and obj.mcq_subtype == Question.COMBINED:
            import re
            lines = obj.question_text.split('\n')
            roman_pattern = re.compile(r'^(i{1,3}|iv|v)\.\s+', re.IGNORECASE)
            statements = []
            for line in lines:
                line = line.strip()
                if roman_pattern.match(line):
                    statements.append(roman_pattern.sub('', line))
            return statements if statements else None
        return None
    
    def get_footer(self, obj):
        """Extract footer for combined MCQ"""
        if obj.type == Question.MCQ and obj.mcq_subtype == Question.COMBINED:
            lines = obj.question_text.split('\n')
            import re
            roman_pattern = re.compile(r'^(i{1,3}|iv|v)\.\s+', re.IGNORECASE)
            found_roman = False
            for line in lines:
                line = line.strip()
                if roman_pattern.match(line):
                    found_roman = True
                elif found_roman and line:
                    return line
            return 'নিচের কোনটি সঠিক?'
        return None
    
    def get_year(self, obj):
        # Extract from tags or return empty
        return ''
    
    def get_chapter(self, obj):
        topics = obj.topics.all()
        if topics:
            return topics[0].chapter.name
        return ''
    
    def get_topic(self, obj):
        topics = obj.topics.all()
        if topics:
            return topics[0].name
        return ''
    
    def get_school(self, obj):
        return ''
    
    def get_schoolYear(self, obj):
        return ''
    
    def get_options(self, obj):
        if obj.type == Question.MCQ:
            return FrontendMCQOptionSerializer(obj.mcq_options.all().order_by('order'), many=True).data
        return None
    
    def get_subQuestions(self, obj):
        if obj.type == Question.CQ:
            return FrontendCQSubQuestionSerializer(obj.cq_sub_questions.all().order_by('order'), many=True).data
        return None

