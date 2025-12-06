from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import (
    Class, Subject, Chapter, Topic, Question, MCQOption, CQSubQuestion
)

User = get_user_model()


class QuestionAPITestCase(APITestCase):
    """Test cases for Question API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
        MCQOption.objects.all().delete()
        CQSubQuestion.objects.all().delete()
        Question.objects.all().delete()
        Topic.objects.all().delete()
        Chapter.objects.all().delete()
        Subject.objects.all().delete()
        Class.objects.all().delete()
        User.objects.all().delete()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test hierarchy
        self.class_obj = Class.objects.create(
            name='Class 6',
            code='CLS6',
            order=6,
            created_by=self.user
        )
        
        self.subject = Subject.objects.create(
            class_level=self.class_obj,
            name='Mathematics',
            code='MATH6',
            order=1,
            created_by=self.user
        )
        
        self.chapter = Chapter.objects.create(
            subject=self.subject,
            name='Algebra',
            order=1,
            created_by=self.user
        )
        
        self.topic = Topic.objects.create(
            chapter=self.chapter,
            name='Linear Equations',
            order=1,
            created_by=self.user
        )
        
        # Create test MCQ question
        self.mcq_question = Question.objects.create(
            type=Question.MCQ,
            mcq_subtype=Question.SIMPLE,
            question_text='What is 2 + 2?',
            marks=1,
            difficulty=Question.EASY,
            subject=self.subject,
            created_by=self.user
        )
        self.mcq_question.topics.add(self.topic)
        
        # Add MCQ options
        MCQOption.objects.create(
            question=self.mcq_question,
            option_label='A',
            option_text='3',
            is_correct=False,
            order=0
        )
        MCQOption.objects.create(
            question=self.mcq_question,
            option_label='B',
            option_text='4',
            is_correct=True,
            order=1
        )
    
    def test_list_questions(self):
        """Test listing all questions"""
        response = self.client.get('/api/questions/questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_questions_by_subject(self):
        """Test listing questions filtered by subject"""
        response = self.client.get(f'/api/questions/questions/?subject_id={self.subject.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_list_questions_by_topic(self):
        """Test listing questions filtered by topic"""
        response = self.client.get(f'/api/questions/questions/?topic_id={self.topic.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_create_mcq_question(self):
        """Test creating a new MCQ question"""
        data = {
            'type': 'mcq',
            'mcq_subtype': 'simple',
            'question_text': 'What is 5 + 3?',
            'marks': 1,
            'difficulty': 'easy',
            'subject_id': str(self.subject.id),
            'topic_ids': [str(self.topic.id)],
            'tags': ['basic', 'addition'],
            'is_public': True,
            'options': [
                {'option_label': 'A', 'option_text': '7', 'is_correct': False},
                {'option_label': 'B', 'option_text': '8', 'is_correct': True},
                {'option_label': 'C', 'option_text': '9', 'is_correct': False},
                {'option_label': 'D', 'option_text': '10', 'is_correct': False}
            ]
        }
        
        response = self.client.post('/api/questions/questions/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['question_text'], 'What is 5 + 3?')
        self.assertEqual(len(response.data['mcq_options']), 4)
    
    def test_create_creative_question(self):
        """Test creating a new Creative question"""
        data = {
            'type': 'cq',
            'question_text': 'Read the passage and answer the questions',
            'marks': 10,
            'difficulty': 'medium',
            'subject_id': str(self.subject.id),
            'topic_ids': [str(self.topic.id)],
            'tags': ['comprehension'],
            'is_public': True,
            'sub_questions': [
                {'label': 'a', 'sub_question_text': 'Question A', 'marks': 2, 'answer': 'Answer A'},
                {'label': 'b', 'sub_question_text': 'Question B', 'marks': 3, 'answer': 'Answer B'},
                {'label': 'c', 'sub_question_text': 'Question C', 'marks': 5, 'answer': 'Answer C'}
            ]
        }
        
        response = self.client.post('/api/questions/questions/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'cq')
        self.assertEqual(len(response.data['cq_sub_questions']), 3)
    
    def test_get_question_detail(self):
        """Test getting question detail"""
        response = self.client.get(f'/api/questions/questions/{self.mcq_question.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question_text'], 'What is 2 + 2?')
        self.assertEqual(len(response.data['mcq_options']), 2)
    
    def test_update_question(self):
        """Test updating a question"""
        data = {
            'question_text': 'What is 2 + 2? (Updated)',
            'difficulty': 'medium'
        }
        
        response = self.client.put(
            f'/api/questions/questions/{self.mcq_question.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question_text'], 'What is 2 + 2? (Updated)')
    
    def test_delete_question(self):
        """Test soft deleting a question"""
        response = self.client.delete(f'/api/questions/questions/{self.mcq_question.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.mcq_question.refresh_from_db()
        self.assertFalse(self.mcq_question.is_active)
    
    def test_verify_question(self):
        """Test verifying a question"""
        response = self.client.post(f'/api/questions/questions/{self.mcq_question.id}/verify/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.mcq_question.refresh_from_db()
        self.assertTrue(self.mcq_question.is_verified)
        self.assertEqual(self.mcq_question.verified_by, self.user)
    
    def test_unverify_question(self):
        """Test unverifying a question"""
        # First verify it
        self.mcq_question.is_verified = True
        self.mcq_question.verified_by = self.user
        self.mcq_question.save()
        
        response = self.client.post(f'/api/questions/questions/{self.mcq_question.id}/unverify/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.mcq_question.refresh_from_db()
        self.assertFalse(self.mcq_question.is_verified)
    
    def test_duplicate_question(self):
        """Test duplicating a question"""
        response = self.client.post(f'/api/questions/questions/{self.mcq_question.id}/duplicate/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)
        
        # Verify duplicated question has same content
        self.assertEqual(response.data['question_text'], self.mcq_question.question_text)
        self.assertFalse(response.data['is_verified'])
    
    def test_get_my_questions(self):
        """Test getting questions created by current user"""
        response = self.client.get('/api/questions/questions/my_questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 1)
    
    def test_get_mcq_questions(self):
        """Test getting only MCQ questions"""
        response = self.client.get('/api/questions/questions/mcq/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 1)
        for question in results:
            self.assertEqual(question['type'], 'mcq')
    
    def test_search_questions(self):
        """Test searching questions"""
        response = self.client.get('/api/questions/questions/?search=What is')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 1)
