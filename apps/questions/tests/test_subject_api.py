from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Subject

User = get_user_model()


class SubjectAPITestCase(APITestCase):
    """Test cases for Subject API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
        Subject.objects.all().delete()
        Class.objects.all().delete()
        User.objects.all().delete()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test class
        self.class_obj = Class.objects.create(
            name='Class 6',
            code='CLS6',
            order=6,
            created_by=self.user
        )
        
        # Create test subjects
        self.subject1 = Subject.objects.create(
            class_level=self.class_obj,
            name='Mathematics',
            code='MATH6',
            order=1,
            created_by=self.user
        )
        self.subject2 = Subject.objects.create(
            class_level=self.class_obj,
            name='Science',
            code='SCI6',
            order=2,
            created_by=self.user
        )
    
    def test_list_subjects(self):
        """Test listing all subjects"""
        response = self.client.get('/api/questions/subjects/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_subjects_by_class(self):
        """Test listing subjects filtered by class"""
        response = self.client.get(f'/api/questions/subjects/?class_id={self.class_obj.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_create_subject(self):
        """Test creating a new subject"""
        data = {
            'class_level': str(self.class_obj.id),
            'name': 'English',
            'code': 'ENG6',
            'description': 'English language',
            'order': 3
        }
        
        response = self.client.post('/api/questions/subjects/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'English')
        self.assertEqual(Subject.objects.count(), 3)
    
    def test_get_subject_detail(self):
        """Test getting subject detail"""
        response = self.client.get(f'/api/questions/subjects/{self.subject1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mathematics')
        self.assertEqual(response.data['class_name'], 'Class 6')
    
    def test_update_subject(self):
        """Test updating a subject"""
        data = {
            'name': 'Mathematics Advanced',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            f'/api/questions/subjects/{self.subject1.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mathematics Advanced')
    
    def test_delete_subject(self):
        """Test soft deleting a subject"""
        response = self.client.delete(f'/api/questions/subjects/{self.subject1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.subject1.refresh_from_db()
        self.assertFalse(self.subject1.is_active)
    
    def test_search_subjects(self):
        """Test searching subjects"""
        response = self.client.get('/api/questions/subjects/?search=Math')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Mathematics')
    
    def test_reorder_subjects(self):
        """Test reordering subjects"""
        data = {
            'class_id': str(self.class_obj.id),
            'subject_orders': [
                {'id': str(self.subject2.id), 'order': 1},
                {'id': str(self.subject1.id), 'order': 2}
            ]
        }
        
        response = self.client.post('/api/questions/subjects/reorder/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.subject1.refresh_from_db()
        self.subject2.refresh_from_db()
        self.assertEqual(self.subject2.order, 1)
        self.assertEqual(self.subject1.order, 2)
