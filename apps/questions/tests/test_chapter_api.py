from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Subject, Chapter

User = get_user_model()


class ChapterAPITestCase(APITestCase):
    """Test cases for Chapter API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
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
        
        # Create test chapters
        self.chapter1 = Chapter.objects.create(
            subject=self.subject,
            name='Algebra',
            description='Basic algebra',
            order=1,
            created_by=self.user
        )
        self.chapter2 = Chapter.objects.create(
            subject=self.subject,
            name='Geometry',
            description='Basic geometry',
            order=2,
            created_by=self.user
        )
    
    def test_list_chapters(self):
        """Test listing all chapters"""
        response = self.client.get('/api/questions/chapters/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_chapters_by_subject(self):
        """Test listing chapters filtered by subject"""
        response = self.client.get(f'/api/questions/chapters/?subject_id={self.subject.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_chapters_by_class(self):
        """Test listing chapters filtered by class"""
        response = self.client.get(f'/api/questions/chapters/?class_id={self.class_obj.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_create_chapter(self):
        """Test creating a new chapter"""
        data = {
            'subject': str(self.subject.id),
            'name': 'Trigonometry',
            'description': 'Basic trigonometry',
            'order': 3
        }
        
        response = self.client.post('/api/questions/chapters/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Trigonometry')
        self.assertEqual(Chapter.objects.count(), 3)
    
    def test_get_chapter_detail(self):
        """Test getting chapter detail"""
        response = self.client.get(f'/api/questions/chapters/{self.chapter1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Algebra')
        self.assertEqual(response.data['subject_name'], 'Mathematics')
    
    def test_update_chapter(self):
        """Test updating a chapter"""
        data = {
            'name': 'Algebra Advanced',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            f'/api/questions/chapters/{self.chapter1.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Algebra Advanced')
    
    def test_delete_chapter(self):
        """Test soft deleting a chapter"""
        response = self.client.delete(f'/api/questions/chapters/{self.chapter1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.chapter1.refresh_from_db()
        self.assertFalse(self.chapter1.is_active)
    
    def test_search_chapters(self):
        """Test searching chapters"""
        response = self.client.get('/api/questions/chapters/?search=Algebra')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Algebra')
    
    def test_reorder_chapters(self):
        """Test reordering chapters"""
        data = {
            'subject_id': str(self.subject.id),
            'chapter_orders': [
                {'id': str(self.chapter2.id), 'order': 1},
                {'id': str(self.chapter1.id), 'order': 2}
            ]
        }
        
        response = self.client.post('/api/questions/chapters/reorder/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.chapter1.refresh_from_db()
        self.chapter2.refresh_from_db()
        self.assertEqual(self.chapter2.order, 1)
        self.assertEqual(self.chapter1.order, 2)
