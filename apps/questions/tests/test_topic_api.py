from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Subject, Chapter, Topic

User = get_user_model()


class TopicAPITestCase(APITestCase):
    """Test cases for Topic API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
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
        
        # Create test topics
        self.topic1 = Topic.objects.create(
            chapter=self.chapter,
            name='Linear Equations',
            description='Solving linear equations',
            order=1,
            created_by=self.user
        )
        self.topic2 = Topic.objects.create(
            chapter=self.chapter,
            name='Quadratic Equations',
            description='Solving quadratic equations',
            order=2,
            created_by=self.user
        )
    
    def test_list_topics(self):
        """Test listing all topics"""
        response = self.client.get('/api/questions/topics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_topics_by_chapter(self):
        """Test listing topics filtered by chapter"""
        response = self.client.get(f'/api/questions/topics/?chapter_id={self.chapter.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_topics_by_subject(self):
        """Test listing topics filtered by subject"""
        response = self.client.get(f'/api/questions/topics/?subject_id={self.subject.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_topics_by_class(self):
        """Test listing topics filtered by class"""
        response = self.client.get(f'/api/questions/topics/?class_id={self.class_obj.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_create_topic(self):
        """Test creating a new topic"""
        data = {
            'chapter': str(self.chapter.id),
            'name': 'Polynomials',
            'description': 'Introduction to polynomials',
            'order': 3
        }
        
        response = self.client.post('/api/questions/topics/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Polynomials')
        self.assertEqual(Topic.objects.count(), 3)
    
    def test_get_topic_detail(self):
        """Test getting topic detail"""
        response = self.client.get(f'/api/questions/topics/{self.topic1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Linear Equations')
        self.assertEqual(response.data['chapter_name'], 'Algebra')
        self.assertEqual(response.data['subject_name'], 'Mathematics')
    
    def test_update_topic(self):
        """Test updating a topic"""
        data = {
            'name': 'Linear Equations Advanced',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            f'/api/questions/topics/{self.topic1.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Linear Equations Advanced')
    
    def test_delete_topic(self):
        """Test soft deleting a topic"""
        response = self.client.delete(f'/api/questions/topics/{self.topic1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.topic1.refresh_from_db()
        self.assertFalse(self.topic1.is_active)
    
    def test_search_topics(self):
        """Test searching topics"""
        response = self.client.get('/api/questions/topics/?search=Linear')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Linear Equations')
    
    def test_reorder_topics(self):
        """Test reordering topics"""
        data = {
            'chapter_id': str(self.chapter.id),
            'topic_orders': [
                {'id': str(self.topic2.id), 'order': 1},
                {'id': str(self.topic1.id), 'order': 2}
            ]
        }
        
        response = self.client.post('/api/questions/topics/reorder/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.topic1.refresh_from_db()
        self.topic2.refresh_from_db()
        self.assertEqual(self.topic2.order, 1)
        self.assertEqual(self.topic1.order, 2)
