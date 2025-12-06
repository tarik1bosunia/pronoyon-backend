from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import (
    Class, Group, Subject, Chapter, Topic,
    Question, MCQOption, CQSubQuestion
)


# ============= Inline Admin Classes =============

class MCQOptionInline(admin.TabularInline):
    model = MCQOption
    extra = 4
    fields = ['option_label', 'option_text', 'is_correct', 'combined_option_indices', 'order']
    ordering = ['order']


class CQSubQuestionInline(admin.StackedInline):
    model = CQSubQuestion
    extra = 1
    fields = ['label', 'sub_question_text', 'marks', 'answer', 'order']
    ordering = ['order']


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ['name', 'order', 'is_active']
    ordering = ['order']
    show_change_link = True


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 0
    fields = ['name', 'order', 'is_active']
    ordering = ['order']
    show_change_link = True


class GroupInline(admin.TabularInline):
    model = Group
    extra = 0
    fields = ['name', 'code', 'group_type', 'order', 'is_active']
    ordering = ['order']
    show_change_link = True


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0
    fields = ['name', 'code', 'group', 'order', 'is_active']
    ordering = ['order']
    show_change_link = True


# ============= Main Admin Classes =============

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'order', 'has_groups', 'group_count', 'subject_count', 'is_active', 'created_at']
    list_filter = ['has_groups', 'is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [GroupInline, SubjectInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'order', 'has_groups')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def group_count(self, obj):
        count = obj.groups.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/group/?class_level__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    group_count.short_description = 'Groups'
    
    def subject_count(self, obj):
        count = obj.subjects.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/subject/?class_level__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    subject_count.short_description = 'Subjects'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'class_level', 'group_type_badge', 'order', 'subject_count', 'is_active', 'created_at']
    list_filter = ['group_type', 'class_level', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'class_level__name']
    ordering = ['class_level__order', 'order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [SubjectInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('class_level', 'name', 'code', 'group_type', 'order')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def group_type_badge(self, obj):
        colors = {
            'science': '#28a745',
            'arts': '#ffc107',
            'commerce': '#17a2b8',
            'general': '#6c757d'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.group_type, '#6c757d'),
            obj.get_group_type_display()
        )
    group_type_badge.short_description = 'Group Type'
    
    def subject_count(self, obj):
        count = obj.subjects.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/subject/?group__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    subject_count.short_description = 'Subjects'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'class_level', 'group', 'order', 'chapter_count', 'question_count', 'is_active', 'created_at']
    list_filter = ['class_level', 'group', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'class_level__name', 'group__name']
    ordering = ['class_level__order', 'group__order', 'order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [ChapterInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('class_level', 'group', 'name', 'code', 'order')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def chapter_count(self, obj):
        count = obj.chapters.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/chapter/?subject__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    chapter_count.short_description = 'Chapters'
    
    def question_count(self, obj):
        count = obj.questions.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/question/?subject__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    question_count.short_description = 'Questions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'class_display', 'order', 'topic_count', 'question_count', 'is_active', 'created_at']
    list_filter = ['subject__class_level', 'subject', 'is_active', 'created_at']
    search_fields = ['name', 'subject__name', 'subject__class_level__name']
    ordering = ['subject__class_level__order', 'subject__order', 'order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [TopicInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'name', 'order')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def class_display(self, obj):
        return obj.subject.class_level.name
    class_display.short_description = 'Class'
    
    def topic_count(self, obj):
        count = obj.topics.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/topic/?chapter__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    topic_count.short_description = 'Topics'
    
    def question_count(self, obj):
        count = Question.objects.filter(topics__chapter=obj, is_active=True).distinct().count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/question/?topics__chapter__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    question_count.short_description = 'Questions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'chapter', 'subject_display', 'class_display', 'order', 'question_count', 'is_active', 'created_at']
    list_filter = ['chapter__subject__class_level', 'chapter__subject', 'chapter', 'is_active', 'created_at']
    search_fields = ['name', 'chapter__name', 'chapter__subject__name']
    ordering = ['chapter__subject__class_level__order', 'chapter__subject__order', 'chapter__order', 'order']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('chapter', 'name', 'order')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def subject_display(self, obj):
        return obj.chapter.subject.name
    subject_display.short_description = 'Subject'
    
    def class_display(self, obj):
        return obj.chapter.subject.class_level.name
    class_display.short_description = 'Class'
    
    def question_count(self, obj):
        count = obj.questions.filter(is_active=True).count()
        if count > 0:
            return format_html(
                '<a href="/admin/questions/question/?topics__id__exact={}" style="color: #417690; font-weight: bold;">{}</a>',
                obj.id, count
            )
        return count
    question_count.short_description = 'Questions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'type_badge', 'difficulty_badge', 'subject', 'marks', 'is_active', 'created_at']
    list_filter = ['type', 'mcq_subtype', 'difficulty', 'subject', 'is_active', 'created_at']
    search_fields = ['question_text', 'subject__name', 'topics__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    filter_horizontal = ['topics']
    
    fieldsets = (
        ('Question Information', {
            'fields': ('type', 'mcq_subtype', 'question_text', 'marks', 'difficulty')
        }),
        ('Subject & Topics', {
            'fields': ('subject', 'topics')
        }),
        ('Solution', {
            'fields': ('solution',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_inlines(self, request, obj):
        if obj and obj.type == Question.MCQ:
            return [MCQOptionInline]
        elif obj and obj.type == Question.CQ:
            return [CQSubQuestionInline]
        return []
    
    def question_preview(self, obj):
        preview = obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
        return format_html('<div style="max-width: 400px;">{}</div>', preview)
    question_preview.short_description = 'Question'
    
    def type_badge(self, obj):
        colors = {
            'mcq': '#007bff',
            'cq': '#28a745'
        }
        label = obj.get_type_display()
        if obj.type == Question.MCQ and obj.mcq_subtype:
            label += f' ({obj.get_mcq_subtype_display()})'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.type, '#6c757d'),
            label
        )
    type_badge.short_description = 'Type'
    
    def difficulty_badge(self, obj):
        colors = {
            'easy': '#28a745',
            'medium': '#ffc107',
            'hard': '#dc3545'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.difficulty, '#6c757d'),
            obj.get_difficulty_display().upper()
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MCQOption)
class MCQOptionAdmin(admin.ModelAdmin):
    list_display = ['option_label', 'option_preview', 'question_preview', 'is_correct_badge', 'order']
    list_filter = ['is_correct', 'question__type', 'question__difficulty']
    search_fields = ['option_text', 'question__question_text']
    ordering = ['question', 'order']
    
    fieldsets = (
        ('Option Information', {
            'fields': ('question', 'option_label', 'option_text', 'is_correct', 'order')
        }),
        ('Combined MCQ', {
            'fields': ('combined_option_indices',),
            'classes': ('collapse',),
            'description': 'For combined MCQ questions, specify which statement indices this option combines (e.g., [0, 1, 2])'
        }),
    )
    
    def option_preview(self, obj):
        preview = obj.option_text[:80] + '...' if len(obj.option_text) > 80 else obj.option_text
        return preview
    option_preview.short_description = 'Option Text'
    
    def question_preview(self, obj):
        preview = obj.question.question_text[:60] + '...' if len(obj.question.question_text) > 60 else obj.question.question_text
        return preview
    question_preview.short_description = 'Question'
    
    def is_correct_badge(self, obj):
        if obj.is_correct:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">✓ CORRECT</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Wrong</span>'
        )
    is_correct_badge.short_description = 'Correct?'


@admin.register(CQSubQuestion)
class CQSubQuestionAdmin(admin.ModelAdmin):
    list_display = ['label', 'sub_question_preview', 'question_preview', 'marks', 'order']
    list_filter = ['question__subject', 'question__difficulty']
    search_fields = ['sub_question_text', 'question__question_text', 'answer']
    ordering = ['question', 'order']
    
    fieldsets = (
        ('Sub-Question Information', {
            'fields': ('question', 'label', 'sub_question_text', 'marks', 'order')
        }),
        ('Answer', {
            'fields': ('answer',)
        }),
    )
    
    def sub_question_preview(self, obj):
        preview = obj.sub_question_text[:80] + '...' if len(obj.sub_question_text) > 80 else obj.sub_question_text
        return preview
    sub_question_preview.short_description = 'Sub-Question'
    
    def question_preview(self, obj):
        preview = obj.question.question_text[:60] + '...' if len(obj.question.question_text) > 60 else obj.question.question_text
        return preview
    question_preview.short_description = 'Main Question'
