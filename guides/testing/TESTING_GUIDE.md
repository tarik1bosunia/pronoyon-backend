# Testing Guide

> Comprehensive testing documentation for ReplyCompass API

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Test Categories](#test-categories)

## 🎯 Overview

The ReplyCompass project includes comprehensive test coverage for:

- **Model Tests**: Database models and business logic
- **API Tests**: REST API endpoints and authentication
- **Service Tests**: Business logic and RBAC services
- **Integration Tests**: End-to-end workflows
- **Selector Tests**: Data query and retrieval logic

### Test Framework

- **Django TestCase**: For database-related tests
- **DRF APIClient**: For API endpoint testing
- **pytest**: Optional test runner with advanced features

## 📁 Test Structure

```
apps/
├── accounts/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py      # User model tests
│       └── test_api.py          # Authentication API tests
├── rbac/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py       # RBAC model tests
│       ├── test_api.py          # RBAC API tests
│       ├── test_services.py     # RBAC service tests
│       └── test_integration.py  # Integration tests
└── core/
    └── tests/
        └── __init__.py
```

## 🚀 Running Tests

### Run All Tests

```bash
# Using Django test runner
docker compose exec web python manage.py test

# Or with make command
make test
```

### Run Specific Test Files

```bash
# Test specific app
docker compose exec web python manage.py test apps.accounts

# Test specific test file
docker compose exec web python manage.py test apps.rbac.tests.test_models

# Test specific test class
docker compose exec web python manage.py test apps.rbac.tests.test_models.RoleModelTestCase

# Test specific test method
docker compose exec web python manage.py test apps.rbac.tests.test_models.RoleModelTestCase.test_create_role
```

### Using pytest (Advanced)

```bash
# Install pytest dependencies first
docker compose exec web pip install -r requirements-test.txt

# Run all tests
docker compose exec web pytest

# Run with coverage
docker compose exec web pytest --cov=apps --cov-report=html

# Run specific tests
docker compose exec web pytest apps/rbac/tests/test_models.py

# Run tests matching pattern
docker compose exec web pytest -k "test_permission"

# Run parallel tests
docker compose exec web pytest -n 4

# Run with verbose output
docker compose exec web pytest -v
```

### Make Commands

```bash
make test           # Run all tests
make test-verbose   # Run tests with verbose output
make coverage       # Run tests with coverage report
```

## 📊 Test Coverage

### Current Coverage

Run coverage report:

```bash
make coverage
```

### Coverage Report

```bash
# Generate HTML coverage report
docker compose exec web pytest --cov=apps --cov-report=html

# View report (opens in browser)
open htmlcov/index.html
```

### Coverage Goals

- **Overall**: > 80%
- **Models**: > 90%
- **Services**: > 85%
- **API Views**: > 80%
- **Selectors**: > 85%

## ✍️ Writing Tests

### Model Tests

```python
from django.test import TestCase
from apps.rbac.models import Role, Permission

class RoleModelTestCase(TestCase):
    """Test Role model"""
    
    def setUp(self):
        """Set up test data"""
        self.permission = Permission.objects.create(
            name='user.view',
            codename='user-view',
            category='user'
        )
    
    def test_create_role(self):
        """Test creating a role"""
        role = Role.objects.create(
            name='Admin',
            slug='admin',
            level=70
        )
        
        self.assertEqual(role.name, 'Admin')
        self.assertEqual(role.level, 70)
        self.assertTrue(role.is_active)
```

### API Tests

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class RoleAPITestCase(TestCase):
    """Test Role API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_roles(self):
        """Test listing roles"""
        url = reverse('role-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Service Tests

```python
from django.test import TestCase
from apps.rbac.services import UserRoleService

class UserRoleServiceTestCase(TestCase):
    """Test UserRoleService"""
    
    def test_assign_role(self):
        """Test assigning role to user"""
        user_role = UserRoleService.assign_role_to_user(
            user=self.user,
            role=self.role
        )
        
        self.assertIsNotNone(user_role)
        self.assertTrue(user_role.is_active)
```

## 🏷️ Test Categories

### Unit Tests

Test individual components in isolation:

- Model methods
- Service functions
- Selector queries
- Utility functions

```python
class PermissionModelTestCase(TestCase):
    """Unit tests for Permission model"""
    
    def test_permission_str_method(self):
        """Test string representation"""
        permission = Permission.objects.create(
            name='user.view',
            codename='user-view',
            category='user'
        )
        self.assertEqual(str(permission), 'user.view (user)')
```

### Integration Tests

Test complete workflows:

- User registration → role assignment → permission check
- Role creation → permission assignment → user access
- Complete RBAC hierarchy

```python
class RBACIntegrationTestCase(TestCase):
    """Integration tests for RBAC system"""
    
    def test_user_promotion_flow(self):
        """Test promoting user through role hierarchy"""
        # Start as guest
        # Promote to user
        # Promote to moderator
        # Verify permissions at each level
```

### API Tests

Test REST API endpoints:

- Authentication (login, logout, token refresh)
- CRUD operations
- Permissions and authorization
- Filtering and pagination

```python
class AuthenticationAPITestCase(TestCase):
    """Test authentication endpoints"""
    
    def test_user_login(self):
        """Test user login"""
        url = reverse('rest_login')
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
```

## 🎯 Test Best Practices

### 1. Test Organization

- One test file per model/view/service
- Group related tests in classes
- Use descriptive test names

### 2. Test Data

- Use `setUp()` for common test data
- Create minimal required data
- Clean up in `tearDown()` if needed

### 3. Assertions

- Use specific assertions (`assertEqual`, `assertIn`, etc.)
- Test both positive and negative cases
- Test edge cases and error conditions

### 4. Test Isolation

- Each test should be independent
- Don't rely on test execution order
- Use transactions (automatic in Django tests)

### 5. Documentation

- Write docstrings for test classes and methods
- Comment complex test logic
- Document test data setup

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Build containers
        run: docker compose build
      
      - name: Run tests
        run: docker compose exec -T web python manage.py test
      
      - name: Generate coverage
        run: docker compose exec -T web pytest --cov=apps --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 🐛 Debugging Tests

### Print Debug Info

```python
def test_example(self):
    role = Role.objects.create(name='Test')
    print(f"Role ID: {role.id}")  # Will show in test output
    print(f"Role permissions: {role.permissions.count()}")
```

### Use pdb

```python
def test_example(self):
    import pdb; pdb.set_trace()
    # Test will pause here for debugging
```

### Run with verbose output

```bash
docker compose exec web python manage.py test --verbosity=2
```

## 📝 Test Checklist

When adding new features, ensure you have:

- [ ] Model tests (CRUD, validation, methods)
- [ ] API tests (endpoints, authentication, permissions)
- [ ] Service tests (business logic)
- [ ] Integration tests (complete workflows)
- [ ] Edge case tests (errors, validation)
- [ ] Documentation updated

## 🔗 Related Documentation

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [DRF Testing Documentation](https://www.django-rest-framework.org/api-guide/testing/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Need help?** Check the [Development Guide](development/DEVELOPMENT.md) or ask in the team chat.
