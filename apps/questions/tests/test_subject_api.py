from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Group, Subject

User = get_user_model()


class SubjectAPITestCase(APITestCase):
    """Test cases for Subject API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Clean all existing data first
        Subject.objects.all().delete()
        Group.objects.all().delete()
        Class.objects.all().delete()
        User.objects.all().delete()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test class without groups
        self.class_obj = Class.objects.create(
            name='Class 6',
            code='CLS6',
            has_groups=False,
            order=6,
            created_by=self.user
        )
        
        # Create test class with groups
        self.hsc_class = Class.objects.create(
            name='HSC',
            code='HSC',
            has_groups=True,
            order=12,
            created_by=self.user
        )
        
        # Create groups for HSC
        self.science_group = Group.objects.create(
            class_level=self.hsc_class,
            name='Science',
            code='SCI',
            group_type=Group.SCIENCE,
            order=1,
            created_by=self.user
        )
        
        self.arts_group = Group.objects.create(
            class_level=self.hsc_class,
            name='Arts',
            code='ARTS',
            group_type=Group.ARTS,
            order=2,
            created_by=self.user
        )
        
        # Create test subjects for Class 6 (no group)
        self.subject1 = Subject.objects.create(
            class_level=self.class_obj,
            group=None,
            name='Mathematics',
            code='MATH6',
            order=1,
            created_by=self.user
        )
        self.subject2 = Subject.objects.create(
            class_level=self.class_obj,
            group=None,
            name='Science',
            code='SCI6',
            order=2,
            created_by=self.user
        )
        
        # Create test subjects for HSC Science group
        self.physics = Subject.objects.create(
            class_level=self.hsc_class,
            group=self.science_group,
            name='Physics',
            code='PHY',
            order=1,
            created_by=self.user
        )
        
        # Create test subject for HSC Arts group
        self.history = Subject.objects.create(
            class_level=self.hsc_class,
            group=self.arts_group,
            name='History',
            code='HIST',
            order=1,
            created_by=self.user
        )
    
    def test_list_subjects(self):
        """Test listing all subjects"""
        response = self.client.get('/api/questions/subjects/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 4)  # 2 for Class 6, 1 for HSC Science, 1 for HSC Arts
    
    def test_list_subjects_by_class(self):
        """Test listing subjects filtered by class"""
        response = self.client.get(f'/api/questions/subjects/?class_id={self.class_obj.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_subjects_by_group(self):
        """Test listing subjects filtered by group"""
        response = self.client.get(f'/api/questions/subjects/?group_id={self.science_group.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Physics')
    
    def test_create_subject_without_group(self):
        """Test creating a new subject without group"""
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
        self.assertIsNone(response.data['group'])
        self.assertEqual(Subject.objects.count(), 5)
    
    def test_create_subject_with_group(self):
        """Test creating a subject with group"""
        data = {
            'class_level': str(self.hsc_class.id),
            'group': str(self.science_group.id),
            'name': 'Chemistry',
            'code': 'CHEM',
            'description': 'Chemistry subject',
            'order': 2
        }
        
        response = self.client.post('/api/questions/subjects/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Chemistry')
        self.assertEqual(str(response.data['group']), str(self.science_group.id))
    
    def test_get_subject_detail(self):
        """Test getting subject detail"""
        response = self.client.get(f'/api/questions/subjects/{self.subject1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mathematics')
        self.assertEqual(response.data['class_name'], 'Class 6')
        self.assertIsNone(response.data['group'])
    
    def test_get_subject_with_group_detail(self):
        """Test getting subject with group detail"""
        response = self.client.get(f'/api/questions/subjects/{self.physics.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Physics')
        self.assertEqual(response.data['class_name'], 'HSC')
        self.assertIsNotNone(response.data['group_info'])
        self.assertEqual(response.data['group_info']['name'], 'Science')
    
    def test_update_subject(self):
        """Test updating a subject"""
        data = {
            'name': 'Mathematics Advanced',
            'description': 'Updated description'
        }
        
        response = self.client.patch(
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
    
    def test_subject_unique_constraint_with_group(self):
        """Test that subject names must be unique within class and group"""
        # Try to create duplicate subject name in same class and group
        data = {
            'class_level': str(self.hsc_class.id),
            'group': str(self.science_group.id),
            'name': 'Physics',  # Duplicate
            'code': 'PHY2'
        }
        
        response = self.client.post('/api/questions/subjects/', data)
        
        # Should fail due to unique constraint
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_subject_same_name_different_groups(self):
        """Test that same subject name can exist in different groups"""
        # Create subject with same name but different group
        data = {
            'class_level': str(self.hsc_class.id),
            'group': str(self.arts_group.id),
            'name': 'Physics',  # Same name as Science group
            'code': 'PHY_ARTS'
        }
        
        response = self.client.post('/api/questions/subjects/', data)
        
        # Should succeed as it's a different group
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_subject_group(self):
        """Test updating subject's group"""
        data = {
            'group': str(self.arts_group.id)
        }
        
        response = self.client.patch(
            f'/api/questions/subjects/{self.physics.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.physics.refresh_from_db()
        self.assertEqual(self.physics.group, self.arts_group)
