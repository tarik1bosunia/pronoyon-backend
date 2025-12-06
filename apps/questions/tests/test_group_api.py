from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.questions.models import Class, Group

User = get_user_model()


class GroupAPITestCase(APITestCase):
    """Test cases for Group API endpoints"""
    
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
        self.hsc_class = Class.objects.create(
            name='HSC',
            code='HSC',
            description='Higher Secondary Certificate',
            has_groups=True,
            order=12,
            created_by=self.user
        )
        
        self.class_6 = Class.objects.create(
            name='Class 6',
            code='CLS6',
            description='Sixth grade',
            has_groups=False,
            order=6,
            created_by=self.user
        )
        
        # Create test groups
        self.science_group = Group.objects.create(
            class_level=self.hsc_class,
            name='Science',
            code='SCI',
            group_type=Group.SCIENCE,
            description='Science stream',
            order=1,
            created_by=self.user
        )
        
        self.arts_group = Group.objects.create(
            class_level=self.hsc_class,
            name='Arts',
            code='ARTS',
            group_type=Group.ARTS,
            description='Arts stream',
            order=2,
            created_by=self.user
        )
    
    def test_list_groups(self):
        """Test listing all groups"""
        response = self.client.get('/api/questions/groups/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_list_groups_by_class(self):
        """Test listing groups for a specific class"""
        response = self.client.get(f'/api/questions/classes/{self.hsc_class.id}/groups/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)
    
    def test_create_group(self):
        """Test creating a new group"""
        data = {
            'class_level': str(self.hsc_class.id),
            'name': 'Commerce',
            'code': 'COM',
            'group_type': 'commerce',
            'description': 'Commerce stream',
            'order': 3
        }
        
        response = self.client.post('/api/questions/groups/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Commerce')
        self.assertEqual(Group.objects.count(), 3)
    
    def test_create_group_for_class_without_groups_flag(self):
        """Test that creating group fails for class with has_groups=False"""
        data = {
            'class_level': str(self.class_6.id),
            'name': 'Invalid Group',
            'code': 'INV',
            'group_type': 'general'
        }
        
        response = self.client.post('/api/questions/groups/', data)
        
        # Should fail or return error
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])
    
    def test_get_group_detail(self):
        """Test getting group detail"""
        response = self.client.get(f'/api/questions/groups/{self.science_group.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Science')
        self.assertEqual(response.data['group_type'], 'science')
    
    def test_update_group(self):
        """Test updating a group"""
        data = {
            'name': 'Science Updated',
            'description': 'Updated description'
        }
        
        response = self.client.patch(
            f'/api/questions/groups/{self.science_group.id}/',
            data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Science Updated')
        
        self.science_group.refresh_from_db()
        self.assertEqual(self.science_group.name, 'Science Updated')
    
    def test_delete_group(self):
        """Test soft deleting a group"""
        response = self.client.delete(f'/api/questions/groups/{self.science_group.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.science_group.refresh_from_db()
        self.assertFalse(self.science_group.is_active)
    
    def test_search_groups(self):
        """Test searching groups"""
        response = self.client.get('/api/questions/groups/?search=Science')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Science')
    
    def test_filter_groups_by_type(self):
        """Test filtering groups by type"""
        response = self.client.get('/api/questions/groups/?group_type=science')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)
        for group in results:
            self.assertEqual(group['group_type'], 'science')
    
    def test_group_ordering(self):
        """Test that groups are ordered correctly"""
        response = self.client.get(f'/api/questions/classes/{self.hsc_class.id}/groups/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        
        # Check ordering by order field
        if len(results) >= 2:
            self.assertEqual(results[0]['name'], 'Science')  # order=1
            self.assertEqual(results[1]['name'], 'Arts')     # order=2
    
    def test_unique_group_name_per_class(self):
        """Test that group names must be unique within a class"""
        data = {
            'class_level': str(self.hsc_class.id),
            'name': 'Science',  # Duplicate name
            'code': 'SCI2',
            'group_type': 'science'
        }
        
        response = self.client.post('/api/questions/groups/', data)
        
        # Should fail due to unique constraint
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GroupSelectorsTestCase(APITestCase):
    """Test cases for Group selectors"""
    
    def setUp(self):
        """Set up test data"""
        from apps.questions.selectors import GroupSelectors
        
        Group.objects.all().delete()
        Class.objects.all().delete()
        User.objects.all().delete()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.hsc = Class.objects.create(
            name='HSC',
            has_groups=True,
            order=12,
            created_by=self.user
        )
        
        self.admission = Class.objects.create(
            name='Admission',
            has_groups=True,
            order=13,
            created_by=self.user
        )
        
        # Create groups for HSC
        self.hsc_science = Group.objects.create(
            class_level=self.hsc,
            name='Science',
            code='SCI',
            group_type=Group.SCIENCE,
            order=1,
            created_by=self.user
        )
        
        self.hsc_arts = Group.objects.create(
            class_level=self.hsc,
            name='Arts',
            code='ARTS',
            group_type=Group.ARTS,
            order=2,
            created_by=self.user
        )
        
        # Create group for Admission
        self.admission_science = Group.objects.create(
            class_level=self.admission,
            name='Science',
            code='SCI',
            group_type=Group.SCIENCE,
            order=1,
            created_by=self.user
        )
        
        self.selectors = GroupSelectors
    
    def test_get_all_groups(self):
        """Test getting all groups"""
        groups = self.selectors.get_all_groups()
        self.assertEqual(groups.count(), 3)
    
    def test_get_group_by_id(self):
        """Test getting group by ID"""
        group = self.selectors.get_group_by_id(str(self.hsc_science.id))
        self.assertEqual(group.name, 'Science')
        self.assertEqual(group.class_level.name, 'HSC')
    
    def test_get_groups_by_class(self):
        """Test getting groups by class"""
        groups = self.selectors.get_groups_by_class(str(self.hsc.id))
        self.assertEqual(groups.count(), 2)
    
    def test_get_groups_by_type(self):
        """Test getting groups by type"""
        groups = self.selectors.get_groups_by_type(Group.SCIENCE)
        self.assertEqual(groups.count(), 2)
    
    def test_check_class_has_groups(self):
        """Test checking if class has groups"""
        self.assertTrue(self.selectors.check_class_has_groups(str(self.hsc.id)))


class GroupServicesTestCase(APITestCase):
    """Test cases for Group services"""
    
    def setUp(self):
        """Set up test data"""
        from apps.questions.services import GroupService
        
        Group.objects.all().delete()
        Class.objects.all().delete()
        User.objects.all().delete()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.hsc = Class.objects.create(
            name='HSC',
            has_groups=True,
            order=12,
            created_by=self.user
        )
        
        self.class_6 = Class.objects.create(
            name='Class 6',
            has_groups=False,
            order=6,
            created_by=self.user
        )
        
        self.service = GroupService
    
    def test_create_group(self):
        """Test creating a group"""
        data = {
            'class_level': str(self.hsc.id),
            'name': 'Science',
            'code': 'SCI',
            'group_type': Group.SCIENCE,
            'description': 'Science stream',
            'order': 1
        }
        
        group = self.service.create_group(user=self.user, data=data)
        
        self.assertEqual(group.name, 'Science')
        self.assertEqual(group.class_level, self.hsc)
    
    def test_create_group_fails_for_non_group_class(self):
        """Test that creating group fails for class without has_groups"""
        data = {
            'class_level': str(self.class_6.id),
            'name': 'Invalid',
            'group_type': Group.GENERAL
        }
        
        with self.assertRaises(ValueError):
            self.service.create_group(user=self.user, data=data)
    
    def test_create_default_groups(self):
        """Test creating default groups for a class"""
        groups = self.service.create_default_groups_for_class(
            class_id=str(self.hsc.id),
            user=self.user
        )
        
        self.assertEqual(len(groups), 3)
        group_names = [g.name for g in groups]
        self.assertIn('Science', group_names)
        self.assertIn('Arts', group_names)
        self.assertIn('Commerce', group_names)
    
    def test_update_group(self):
        """Test updating a group"""
        group = Group.objects.create(
            class_level=self.hsc,
            name='Science',
            code='SCI',
            group_type=Group.SCIENCE,
            created_by=self.user
        )
        
        data = {'name': 'Science Updated'}
        updated_group = self.service.update_group(
            group_id=str(group.id),
            data=data
        )
        
        self.assertEqual(updated_group.name, 'Science Updated')
    
    def test_delete_group(self):
        """Test soft deleting a group"""
        group = Group.objects.create(
            class_level=self.hsc,
            name='Science',
            created_by=self.user
        )
        
        self.service.delete_group(group_id=str(group.id))
        
        group.refresh_from_db()
        self.assertFalse(group.is_active)
