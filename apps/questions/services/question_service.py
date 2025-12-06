from typing import Dict, Any, List
from django.db import transaction
from decimal import Decimal
from apps.questions.models import Question, MCQOption, CQSubQuestion


class QuestionService:
    """Service for Question model operations"""
    
    @staticmethod
    @transaction.atomic
    def create_mcq_question(*, user, data: Dict[str, Any]) -> Question:
        """Create a new MCQ question"""
        question = Question.objects.create(
            type=Question.MCQ,
            mcq_subtype=data.get('mcq_subtype', Question.SIMPLE),
            question_text=data['question_text'],
            marks=Decimal(str(data.get('marks', '1.0'))),
            difficulty=data.get('difficulty', Question.MEDIUM),
            subject_id=data['subject_id'],
            solution=data.get('solution', ''),
            hints=data.get('hints', []),
            tags=data.get('tags', []),
            created_by=user,
            is_public=data.get('is_public', True)
        )
        
        # Add topics
        if 'topic_ids' in data:
            question.topics.set(data['topic_ids'])
        
        # Create MCQ options
        if 'options' in data:
            for idx, option_data in enumerate(data['options']):
                MCQOption.objects.create(
                    question=question,
                    option_text=option_data['option_text'],
                    option_label=option_data['option_label'],
                    is_correct=option_data.get('is_correct', False),
                    order=idx,
                    combined_option_indices=option_data.get('combined_option_indices', [])
                )
        
        return question
    
    @staticmethod
    @transaction.atomic
    def create_creative_question(*, user, data: Dict[str, Any]) -> Question:
        """Create a new Creative question"""
        question = Question.objects.create(
            type=Question.CQ,
            question_text=data['question_text'],
            marks=Decimal(str(data.get('marks', '10.0'))),
            difficulty=data.get('difficulty', Question.MEDIUM),
            subject_id=data['subject_id'],
            solution=data.get('solution', ''),
            hints=data.get('hints', []),
            tags=data.get('tags', []),
            created_by=user,
            is_public=data.get('is_public', True)
        )
        
        # Add topics
        if 'topic_ids' in data:
            question.topics.set(data['topic_ids'])
        
        # Create sub-questions
        if 'sub_questions' in data:
            for idx, sub_q_data in enumerate(data['sub_questions']):
                CQSubQuestion.objects.create(
                    question=question,
                    label=sub_q_data['label'],
                    sub_question_text=sub_q_data['sub_question_text'],
                    marks=Decimal(str(sub_q_data.get('marks', '1.0'))),
                    answer=sub_q_data.get('answer', ''),
                    order=idx
                )
        
        return question
    
    @staticmethod
    @transaction.atomic
    def update_question(*, question_id: str, data: Dict[str, Any]) -> Question:
        """Update a question"""
        question = Question.objects.get(id=question_id)
        
        # Update basic fields
        if 'question_text' in data:
            question.question_text = data['question_text']
        if 'marks' in data:
            question.marks = Decimal(str(data['marks']))
        if 'difficulty' in data:
            question.difficulty = data['difficulty']
        if 'subject_id' in data:
            question.subject_id = data['subject_id']
        if 'solution' in data:
            question.solution = data['solution']
        if 'hints' in data:
            question.hints = data['hints']
        if 'tags' in data:
            question.tags = data['tags']
        if 'is_public' in data:
            question.is_public = data['is_public']
        if 'is_active' in data:
            question.is_active = data['is_active']
        
        question.save()
        
        # Update topics
        if 'topic_ids' in data:
            question.topics.set(data['topic_ids'])
        
        # Update MCQ options
        if 'options' in data and question.type == Question.MCQ:
            question.mcq_options.all().delete()
            for idx, option_data in enumerate(data['options']):
                MCQOption.objects.create(
                    question=question,
                    option_text=option_data['option_text'],
                    option_label=option_data['option_label'],
                    is_correct=option_data.get('is_correct', False),
                    order=idx,
                    combined_option_indices=option_data.get('combined_option_indices', [])
                )
        
        # Update CQ sub-questions
        if 'sub_questions' in data and question.type == Question.CQ:
            question.cq_sub_questions.all().delete()
            for idx, sub_q_data in enumerate(data['sub_questions']):
                CQSubQuestion.objects.create(
                    question=question,
                    label=sub_q_data['label'],
                    sub_question_text=sub_q_data['sub_question_text'],
                    marks=Decimal(str(sub_q_data.get('marks', '1.0'))),
                    answer=sub_q_data.get('answer', ''),
                    order=idx
                )
        
        return question
    
    @staticmethod
    @transaction.atomic
    def delete_question(*, question_id: str) -> None:
        """Soft delete a question"""
        question = Question.objects.get(id=question_id)
        question.is_active = False
        question.save()
    
    @staticmethod
    @transaction.atomic
    def verify_question(*, question_id: str, user) -> Question:
        """Verify a question"""
        question = Question.objects.get(id=question_id)
        question.is_verified = True
        question.verified_by = user
        question.save()
        return question
    
    @staticmethod
    @transaction.atomic
    def unverify_question(*, question_id: str) -> Question:
        """Unverify a question"""
        question = Question.objects.get(id=question_id)
        question.is_verified = False
        question.verified_by = None
        question.save()
        return question
    
    @staticmethod
    @transaction.atomic
    def duplicate_question(*, question_id: str, user) -> Question:
        """Duplicate a question"""
        original = Question.objects.prefetch_related(
            'mcq_options',
            'cq_sub_questions',
            'topics'
        ).get(id=question_id)
        
        # Create new question
        new_question = Question.objects.create(
            type=original.type,
            mcq_subtype=original.mcq_subtype,
            question_text=original.question_text,
            marks=original.marks,
            difficulty=original.difficulty,
            subject=original.subject,
            solution=original.solution,
            hints=original.hints,
            tags=original.tags,
            created_by=user,
            is_public=original.is_public,
            is_verified=False
        )
        
        # Copy topics
        new_question.topics.set(original.topics.all())
        
        # Copy MCQ options
        if original.type == Question.MCQ:
            for option in original.mcq_options.all():
                MCQOption.objects.create(
                    question=new_question,
                    option_text=option.option_text,
                    option_label=option.option_label,
                    is_correct=option.is_correct,
                    order=option.order,
                    combined_option_indices=option.combined_option_indices
                )
        
        # Copy CQ sub-questions
        if original.type == Question.CQ:
            for sub_q in original.cq_sub_questions.all():
                CQSubQuestion.objects.create(
                    question=new_question,
                    label=sub_q.label,
                    sub_question_text=sub_q.sub_question_text,
                    marks=sub_q.marks,
                    answer=sub_q.answer,
                    order=sub_q.order
                )
        
        return new_question
