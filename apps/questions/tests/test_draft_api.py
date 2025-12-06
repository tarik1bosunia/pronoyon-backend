from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import (
    Class, Subject, Chapter, Topic, Question, UserDraft, DraftQuestion
)

User = get_user_model()


class DraftAPITestCase(APITestCase):
    """Test cases for Draft API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
        DraftQuestion.objects.all().delete()
        UserDraft.objects.all().delete()
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
        
        # Create test question
        self.question = Question.objects.create(
            type=Question.MCQ,
            question_text='What is 2 + 2?',
            marks=1,
            difficulty=Question.EASY,
            subject=self.subject,
            created_by=self.user
        )
        
        # Create test draft
        self.draft = UserDraft.objects.create(
            user=self.user,
            title='Mid-term Exam',
            description='Questions for mid-term'
        )
        
        # Add question to draft
        DraftQuestion.objects.create(
            draft=self.draft,
            question=self.question,
            order=0,
            notes='Important question'
        )
    
    def test_list_drafts(self):
        """Test listing user's drafts"""
        response = self.client.get('/api/questions/drafts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
    
    def test_list_favorite_drafts(self):
        """Test listing favorite drafts"""
        # Mark draft as favorite
        self.draft.is_favorite = True
        self.draft.save()
        
        response = self.client.get('/api/questions/drafts/?favorites=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
    
    def test_create_draft(self):
        """Test creating a new draft"""
        data = {
            'title': 'Final Exam',
            'description': 'Questions for final exam',
            'is_favorite': False
        }
        
        response = self.client.post('/api/questions/drafts/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Final Exam')
        self.assertEqual(UserDraft.objects.count(), 2)
    
    def test_get_draft_detail(self):
        """Test getting draft detail with questions"""
        response = self.client.get(f'/api/questions/drafts/{self.draft.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Mid-term Exam')
        self.assertEqual(len(response.data['draft_questions']), 1)
    
    def test_update_draft(self):
        """Test updating a draft"""
        data = {
            'title': 'Mid-term Exam Updated',
            'description': 'Updated description'
        }
        
        response = self.client.put(f'/api/questions/drafts/{self.draft.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Mid-term Exam Updated')
    
    def test_delete_draft(self):
        """Test deleting a draft"""
        response = self.client.delete(f'/api/questions/drafts/{self.draft.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserDraft.objects.count(), 0)
    
    def test_add_question_to_draft(self):
        """Test adding a question to draft"""
        # Create another question
        question2 = Question.objects.create(
            type=Question.MCQ,
            question_text='What is 5 + 5?',
            marks=1,
            difficulty=Question.EASY,
            subject=self.subject,
            created_by=self.user
        )
        
        data = {
            'question_id': str(question2.id),
            'notes': 'Also important'
        }
        
        response = self.client.post(
            f'/api/questions/drafts/{self.draft.id}/add_question/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DraftQuestion.objects.filter(draft=self.draft).count(), 2)
    
    def test_add_multiple_questions_to_draft(self):
        """Test adding multiple questions to draft"""
        # Create more questions
        question2 = Question.objects.create(
            type=Question.MCQ,
            question_text='What is 3 + 3?',
            marks=1,
            difficulty=Question.EASY,
            subject=self.subject,
            created_by=self.user
        )
        question3 = Question.objects.create(
            type=Question.MCQ,
            question_text='What is 4 + 4?',
            marks=1,
            difficulty=Question.EASY,
            subject=self.subject,
            created_by=self.user
        )
        
        data = {
            'question_ids': [str(question2.id), str(question3.id)]
        }
        
        response = self.client.post(
            f'/api/questions/drafts/{self.draft.id}/add_multiple_questions/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DraftQuestion.objects.filter(draft=self.draft).count(), 3)
    
    def test_remove_question_from_draft(self):
        """Test removing a question from draft"""
        data = {
            'question_id': str(self.question.id)
        }
        
        response = self.client.post(
            f'/api/questions/drafts/{self.draft.id}/remove_question/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DraftQuestion.objects.filter(draft=self.draft).count(), 0)
    
    def test_update_question_notes(self):
        """Test updating notes for a question in draft"""
        data = {
            'question_id': str(self.question.id),
            'notes': 'Updated notes'
        }
        
        response = self.client.post(
            f'/api/questions/drafts/{self.draft.id}/update_question_notes/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        draft_question = DraftQuestion.objects.get(
            draft=self.draft,
            question=self.question
        )
        self.assertEqual(draft_question.notes, 'Updated notes')
    
    def test_toggle_favorite(self):
        """Test toggling favorite status"""
        self.assertFalse(self.draft.is_favorite)
        
        response = self.client.post(f'/api/questions/drafts/{self.draft.id}/toggle_favorite/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.is_favorite)
    
    def test_clear_draft(self):
        """Test clearing all questions from draft"""
        response = self.client.post(f'/api/questions/drafts/{self.draft.id}/clear/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DraftQuestion.objects.filter(draft=self.draft).count(), 0)
    
    def test_search_drafts(self):
        """Test searching drafts"""
        response = self.client.get('/api/questions/drafts/?search=mid')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Mid-term Exam')
    
    def test_reorder_questions_in_draft(self):
        """Test reordering questions in draft"""
        # Add another question
        question2 = Question.objects.create(
            type=Question.MCQ,
            question_text='What is 5 + 5?',
            marks=1,
            difficulty=Question.EASY,
            subject=self.subject,
            created_by=self.user
        )
        DraftQuestion.objects.create(
            draft=self.draft,
            question=question2,
            order=1
        )
        
        data = {
            'question_orders': [
                {'question_id': str(question2.id), 'order': 0},
                {'question_id': str(self.question.id), 'order': 1}
            ]
        }
        
        response = self.client.post(
            f'/api/questions/drafts/{self.draft.id}/reorder_questions/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
