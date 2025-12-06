from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Group

User = get_user_model()


class ClassAPITestCase(APITestCase):
    """Test cases for Class API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
        Group.objects.all().delete()
        Class.objects.all().delete()
        User.objects.all().delete()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test classes
        self.class1 = Class.objects.create(
            name='Class 6',
            code='CLS6',
            description='Sixth grade',
            has_groups=False,
            order=6,
            created_by=self.user
        )
        self.class2 = Class.objects.create(
            name='Class 7',
            code='CLS7',
            description='Seventh grade',
            has_groups=False,
            order=7,
            created_by=self.user
        )
        self.hsc_class = Class.objects.create(
            name='HSC',
            code='HSC',
            description='Higher Secondary Certificate',
            has_groups=True,
            order=12,
            created_by=self.user
        )
    
    def test_list_classes(self):
        """Test listing all classes"""
        response = self.client.get('/api/questions/classes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 3)
    
    def test_create_class(self):
        """Test creating a new class"""
        data = {
            'name': 'Class 8',
            'code': 'CLS8',
            'description': 'Eighth grade',
            'has_groups': False,
            'order': 8
        }
        
        response = self.client.post('/api/questions/classes/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Class 8')
        self.assertEqual(response.data['has_groups'], False)
        self.assertEqual(Class.objects.count(), 4)
    
    def test_create_class_with_groups(self):
        """Test creating a class with groups enabled"""
        data = {
            'name': 'Admission',
            'code': 'ADM',
            'description': 'Admission test preparation',
            'has_groups': True,
            'order': 13
        }
        
        response = self.client.post('/api/questions/classes/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['has_groups'], True)
    
    def test_get_class_detail(self):
        """Test getting class detail"""
        response = self.client.get(f'/api/questions/classes/{self.class1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Class 6')
        self.assertEqual(response.data['code'], 'CLS6')
    
    def test_update_class(self):
        """Test updating a class"""
        data = {
            'name': 'Class 6 Updated',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            f'/api/questions/classes/{self.class1.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Class 6 Updated')
        
        self.class1.refresh_from_db()
        self.assertEqual(self.class1.name, 'Class 6 Updated')
    
    def test_delete_class(self):
        """Test soft deleting a class"""
        response = self.client.delete(f'/api/questions/classes/{self.class1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.class1.refresh_from_db()
        self.assertFalse(self.class1.is_active)
    
    def test_search_classes(self):
        """Test searching classes"""
        response = self.client.get('/api/questions/classes/?search=Class 6')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Class 6')
    
    def test_reorder_classes(self):
        """Test reordering classes"""
        data = {
            'class_orders': [
                {'id': str(self.class2.id), 'order': 1},
                {'id': str(self.class1.id), 'order': 2}
            ]
        }
        
        response = self.client.post('/api/questions/classes/reorder/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.class1.refresh_from_db()
        self.class2.refresh_from_db()
        self.assertEqual(self.class2.order, 1)
        self.assertEqual(self.class1.order, 2)
    
    def test_create_class_unauthenticated(self):
        """Test creating class without authentication"""
        self.client.force_authenticate(user=None)
        
        data = {'name': 'Class 9', 'code': 'CLS9'}
        response = self.client.post('/api/questions/classes/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_class_with_groups_flag(self):
        """Test that has_groups flag is properly returned"""
        response = self.client.get(f'/api/questions/classes/{self.hsc_class.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_groups'])
    
    def test_class_without_groups_flag(self):
        """Test that has_groups flag is False for regular classes"""
        response = self.client.get(f'/api/questions/classes/{self.class1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_groups'])
    
    def test_update_class_has_groups(self):
        """Test updating has_groups flag"""
        data = {'has_groups': True}
        
        response = self.client.patch(
            f'/api/questions/classes/{self.class1.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_groups'])
        
        self.class1.refresh_from_db()
        self.assertTrue(self.class1.has_groups)
