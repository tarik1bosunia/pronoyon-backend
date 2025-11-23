# Role-Based Access Control (RBAC) System

## Overview

ReplyCompass uses a comprehensive Role-Based Access Control (RBAC) system to manage user permissions and access levels. This system provides granular control over what users can do within the application.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Architecture](#architecture)
3. [Selectors & Services Pattern](#selectors--services-pattern)
4. [Quick Start](#quick-start)
5. [Usage Examples](#usage-examples)
6. [API Endpoints](#api-endpoints)
7. [Best Practices](#best-practices)

---

## Core Concepts

### Permissions

Permissions are the smallest unit of access control. They define specific actions users can perform.

**Format**: `resource.action` (e.g., `user.create`, `content.delete`)

**Categories**:
- `user` - User Management
- `content` - Content Management
- `analytics` - Analytics & Reports
- `settings` - Settings & Configuration
- `billing` - Billing & Payments
- `support` - Customer Support
- `api` - API Access
- `admin` - Administration

### Roles

Roles are collections of permissions. Users are assigned roles, which grant them specific permissions.

**Role Hierarchy** (Level 0-90):
- **Level 0**: Guest
- **Level 10**: User (default for new users)
- **Level 20**: Premium User
- **Level 30**: Moderator
- **Level 40**: Content Manager
- **Level 50**: Support Agent
- **Level 60**: Manager
- **Level 70**: Admin
- **Level 80**: Super Admin
- **Level 90**: System

### Role Inheritance

Roles can inherit permissions from parent roles. For example:
- **Content Manager** inherits from **Moderator**
- **Admin** inherits from **Manager**

### User Roles

Users can have multiple roles with different contexts:
- **Primary Role**: Main role displayed for the user
- **Additional Roles**: Additional access grants
- **Context-Based**: Roles can be scoped to specific contexts (workspace, project, etc.)
- **Expiration**: Roles can have expiration dates

---

## Architecture

### Models

#### Permission
```python
class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    codename = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
```

#### Role
```python
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    role_type = models.CharField(max_length=20)  # system, custom, temporary
    level = models.IntegerField(default=10)
    permissions = models.ManyToManyField(Permission)
    inherits_from = models.ForeignKey('self', null=True)
    is_default = models.BooleanField(default=False)
    max_users = models.IntegerField(null=True)  # Optional limit
```

#### UserRole
```python
class UserRole(models.Model):
    user = models.ForeignKey(CustomUser)
    role = models.ForeignKey(Role)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(CustomUser)
    expires_at = models.DateTimeField(null=True)
    context = models.JSONField(default=dict)
```

#### RoleHistory
Tracks all role assignments, revocations, and modifications for audit purposes.

---

## Selectors & Services Pattern

This RBAC system follows the **Selectors and Services** architectural pattern for clean separation of concerns:

- **Selectors (`apps/rbac/selectors.py`)**: Data access layer - pure functions for querying data
- **Services (`apps/rbac/services.py`)**: Business logic layer - handles operations, validations, transactions
- **Models (`apps/rbac/models.py`)**: Data layer - database structure

### Quick Example

```python
# ✅ Use selectors for reading data
from apps.rbac.selectors import UserRoleSelectors
roles = UserRoleSelectors.get_user_active_roles(user)

# ✅ Use services for writing data
from apps.rbac.services import UserRoleService
UserRoleService.assign_role_to_user(user, admin_role, assigned_by=current_user)

# ✅ Use services for permission checks
from apps.rbac.services import PermissionCheckService
has_access = PermissionCheckService.user_has_permission(user, 'admin.access')
```

📖 **For complete documentation on selectors and services, see [RBAC_SELECTORS_SERVICES_GUIDE.md](./RBAC_SELECTORS_SERVICES_GUIDE.md)**

---

## Quick Start

### 1. Initial Setup

After creating the database, seed the RBAC system:

```bash
python manage.py seed_rbac
```

This creates:
- 35+ pre-defined permissions
- 9 system roles with proper hierarchy
- Permission assignments for each role

### 2. Update Settings

Add RBAC apps to `INSTALLED_APPS` in `config/settings/base.py`:

```python
LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.rbac',  # Add this
]
```

Set the custom user model:

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

### 3. Add Middleware (Optional)

For URL-based permission checking:

```python
MIDDLEWARE = [
    # ... other middleware
    'apps.rbac.middleware.RBACMiddleware',
    'apps.rbac.middleware.RoleExpirationMiddleware',
]

# Configure URL patterns that require permissions
RBAC_URL_PERMISSIONS = {
    '/api/admin/': 'admin.access',
    '/api/users/': 'user.view',
    '/api/analytics/': 'analytics.view',
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Usage Examples

### Check User Permissions

```python
# Check single permission
if request.user.has_permission('user.create'):
    # Create user
    pass

# Check any permission
if request.user.has_any_permission(['user.create', 'user.update']):
    # User can create OR update
    pass

# Check all permissions
if request.user.has_all_permissions(['user.create', 'user.delete']):
    # User can create AND delete
    pass

# Check role
if request.user.has_role('admin'):
    # User is admin
    pass

# Get role level
level = request.user.get_role_level()  # Returns integer 0-90
```

### Assign/Revoke Roles

```python
from apps.rbac.models import Role

# Assign role
role = Role.objects.get(slug='moderator')
request.user.assign_role(
    role=role,
    assigned_by=admin_user,
    expires_at=None,  # Never expires
    is_primary=True
)

# Revoke role
request.user.revoke_role('moderator')

# Get user's active roles
active_roles = request.user.get_active_roles()

# Get primary role
primary_role = request.user.get_primary_role()

# Get all permissions
permissions = request.user.get_all_permissions()
```

### Django Views - Decorators

```python
from apps.rbac.decorators import (
    permission_required,
    any_permission_required,
    role_required,
    minimum_role_level
)

# Single permission
@permission_required('user.create')
def create_user(request):
    # Only users with 'user.create' permission can access
    pass

# Multiple permissions (any)
@any_permission_required(['user.create', 'user.update'])
def manage_user(request):
    # Users need at least one of these permissions
    pass

# Role required
@role_required('admin')
def admin_dashboard(request):
    # Only admins can access
    pass

# Minimum role level
@minimum_role_level(50)  # Manager level
def manager_panel(request):
    # Users with role level >= 50 can access
    pass
```

### DRF Views - Permission Classes

```python
from rest_framework import viewsets
from apps.rbac.permissions import (
    HasPermission,
    HasAnyPermission,
    HasRole,
    MinimumRoleLevel,
    IsOwnerOrHasPermission
)

# Single permission
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [HasPermission]
    permission_required = 'user.create'

# Multiple permissions (any)
class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAnyPermission]
    permissions_required = ['content.create', 'content.update']

# Role required
class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRole]
    role_required = 'admin'

# Minimum role level
class ManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [MinimumRoleLevel]
    minimum_role_level = 60  # Manager level

# Owner or has permission
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrHasPermission]
    permission_required = 'content.update'
    owner_field = 'author'  # Field that references the owner
```

### Custom Permissions

```python
from apps.rbac.models import Permission, Role

# Create custom permission
permission = Permission.objects.create(
    name='project.manage',
    codename='project-manage',
    description='Manage projects',
    category='content',
    is_active=True
)

# Create custom role
role = Role.objects.create(
    name='Project Manager',
    slug='project-manager',
    description='Manages projects',
    role_type='custom',
    level=45,
    is_active=True
)

# Assign permissions to role
role.permissions.add(permission)

# Assign role to user
user.assign_role(role)
```

### Context-Based Roles

```python
# Assign role with specific context (e.g., workspace-specific)
user.assign_role(
    role='manager',
    context={'workspace_id': 123},
    assigned_by=admin
)

# Check in view
user_role = UserRole.objects.filter(
    user=request.user,
    role__slug='manager',
    context__workspace_id=workspace_id,
    is_active=True
).exists()
```

### Temporary Roles

```python
from django.utils import timezone
from datetime import timedelta

# Assign role that expires in 30 days
user.assign_role(
    role='premium-user',
    expires_at=timezone.now() + timedelta(days=30),
    assigned_by=admin
)
```

---

## API Endpoints

### Base URL: `/api/rbac/`

#### Permissions

```http
GET /api/rbac/permissions/
GET /api/rbac/permissions/{id}/
GET /api/rbac/permissions/by_category/
```

#### Roles

```http
GET /api/rbac/roles/
POST /api/rbac/roles/
GET /api/rbac/roles/{slug}/
PUT /api/rbac/roles/{slug}/
PATCH /api/rbac/roles/{slug}/
DELETE /api/rbac/roles/{slug}/
GET /api/rbac/roles/{slug}/permissions/
GET /api/rbac/roles/{slug}/users/
GET /api/rbac/roles/hierarchy/
```

#### User Roles

```http
GET /api/rbac/user-roles/?user_id={id}
POST /api/rbac/user-roles/
GET /api/rbac/user-roles/{id}/
PUT /api/rbac/user-roles/{id}/
DELETE /api/rbac/user-roles/{id}/
POST /api/rbac/user-roles/{id}/revoke/
POST /api/rbac/user-roles/{id}/set_primary/
```

#### Current User

```http
GET /api/rbac/me/permissions/
POST /api/rbac/me/check_permission/
POST /api/rbac/me/check_role/
```

#### Role History

```http
GET /api/rbac/history/?user_id={id}
GET /api/rbac/history/{id}/
```

### Example API Requests

#### Check Current User's Permissions

```bash
curl -X GET http://localhost:8000/api/rbac/me/permissions/ \
  -H "Authorization: Bearer {token}"
```

Response:
```json
{
  "permissions": [
    {"id": 1, "name": "user.view", "codename": "user-view", "category": "user"},
    {"id": 2, "name": "content.create", "codename": "content-create", "category": "content"}
  ],
  "roles": [
    {"id": 1, "name": "User", "slug": "user", "level": 10}
  ],
  "primary_role": {"id": 1, "name": "User", "slug": "user", "level": 10},
  "role_level": 10
}
```

#### Check Specific Permission

```bash
curl -X POST http://localhost:8000/api/rbac/me/check_permission/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"permission": "user.create"}'
```

Response:
```json
{
  "permission": "user.create",
  "has_permission": true
}
```

#### Assign Role to User

```bash
curl -X POST http://localhost:8000/api/rbac/user-roles/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 123,
    "role_id": 3,
    "is_primary": true,
    "expires_at": null
  }'
```

---

## Best Practices

### 1. Use Appropriate Permission Granularity

✅ **Good**: `user.create`, `user.update`, `user.delete`, `user.view`
❌ **Bad**: `user.manage` (too broad), `user.create.with.email` (too specific)

### 2. Follow Naming Conventions

- Permissions: `resource.action` (lowercase)
- Role slugs: `kebab-case`
- Role names: `Title Case`

### 3. Use Role Inheritance

Instead of duplicating permissions:

```python
# Good: Use inheritance
content_manager = Role.objects.create(
    name='Content Manager',
    level=40,
    inherits_from=moderator_role  # Inherits moderator permissions
)

# Bad: Duplicate all permissions
content_manager.permissions.add(*moderator_role.permissions.all())
```

### 4. Prefer Permission Checks Over Role Checks

```python
# Good: Check specific capability
if user.has_permission('user.create'):
    create_user()

# Less flexible: Check role
if user.has_role('admin'):
    create_user()
```

### 5. Use Middleware for Common Patterns

Instead of adding decorators to every view:

```python
# settings.py
RBAC_URL_PERMISSIONS = {
    '/api/admin/': 'admin.access',
    '/api/analytics/': 'analytics.view',
}
```

### 6. Audit Trail

The `RoleHistory` model automatically tracks all role changes. Use it for:
- Compliance requirements
- Debugging access issues
- User activity monitoring

### 7. Regular Permission Reviews

```python
# Get users with high-level roles
admins = UserRole.objects.filter(
    role__level__gte=70,
    is_active=True
)

# Review expired roles
from django.utils import timezone
expired = UserRole.objects.filter(
    expires_at__lt=timezone.now(),
    is_active=True
)
```

### 8. Testing

Always test permission logic:

```python
from django.test import TestCase
from apps.accounts.models import CustomUser
from apps.rbac.models import Role, Permission

class RBACTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('test@example.com')
        self.role = Role.objects.get(slug='user')
        self.user.assign_role(self.role)
    
    def test_user_has_permission(self):
        self.assertTrue(self.user.has_permission('content.view'))
    
    def test_user_lacks_admin_permission(self):
        self.assertFalse(self.user.has_permission('admin.access'))
```

---

## Troubleshooting

### User Can't Access Resource

1. Check if user is authenticated
2. Verify user has active roles: `user.get_active_roles()`
3. Check role has required permission: `role.get_all_permissions()`
4. Verify permission is active: `permission.is_active`
5. Check for expired roles: `user_role.is_expired()`

### Permission Not Working

1. Run `python manage.py seed_rbac` to ensure permissions exist
2. Check permission name format: `resource.action`
3. Verify middleware is configured correctly
4. Check if superuser (bypasses all permission checks)

### Role Not Inheriting Permissions

1. Verify `inherits_from` is set correctly
2. Check for circular inheritance
3. Ensure parent role is active
4. Use `role.get_all_permissions()` to see inherited permissions

---

## Migration Notes

When migrating from another auth system:

1. Map existing roles to new role hierarchy
2. Create custom permissions for unique requirements
3. Batch assign roles using management commands
4. Test thoroughly in staging environment
5. Maintain audit trail during migration

---

## Support

For issues or questions:
- Check Django admin: `/admin/rbac/`
- Review role history: `/admin/rbac/rolehistory/`
- API documentation: `/api/docs/` (Swagger/OpenAPI)

