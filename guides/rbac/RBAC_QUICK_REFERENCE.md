# RBAC Quick Reference

## Permission Check Methods

### User Model Methods

```python
# Check single permission
user.has_permission('user.create')  # Returns: bool

# Check multiple permissions (any)
user.has_any_permission(['user.create', 'user.update'])  # Returns: bool

# Check multiple permissions (all)
user.has_all_permissions(['user.create', 'user.delete'])  # Returns: bool

# Check role
user.has_role('admin')  # Returns: bool

# Get role level
user.get_role_level()  # Returns: int (0-90)

# Get active roles
user.get_active_roles()  # Returns: QuerySet<UserRole>

# Get primary role
user.get_primary_role()  # Returns: Role or None

# Get all permissions
user.get_all_permissions()  # Returns: QuerySet<Permission>

# Assign role
user.assign_role(
    role='admin',  # Role instance or slug
    assigned_by=admin_user,
    expires_at=None,
    context={},
    is_primary=False
)

# Revoke role
user.revoke_role('admin')  # Role instance or slug
```

## Django View Decorators

```python
from apps.rbac.decorators import (
    permission_required,
    any_permission_required,
    all_permissions_required,
    role_required,
    any_role_required,
    minimum_role_level
)

# Single permission
@permission_required('user.create')
def my_view(request):
    pass

# Multiple permissions (any)
@any_permission_required(['user.create', 'user.update'])
def my_view(request):
    pass

# Multiple permissions (all)
@all_permissions_required(['user.create', 'user.delete'])
def my_view(request):
    pass

# Single role
@role_required('admin')
def my_view(request):
    pass

# Multiple roles (any)
@any_role_required(['admin', 'moderator'])
def my_view(request):
    pass

# Minimum role level
@minimum_role_level(50)  # Manager level
def my_view(request):
    pass

# With redirect instead of 403
@permission_required('user.create', raise_exception=False, redirect_url='/login/')
def my_view(request):
    pass
```

## DRF Permission Classes

```python
from apps.rbac.permissions import (
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
    HasRole,
    HasAnyRole,
    MinimumRoleLevel,
    IsOwnerOrHasPermission
)

# Single permission
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasPermission]
    permission_required = 'user.create'

# Multiple permissions (any)
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAnyPermission]
    permissions_required = ['user.create', 'user.update']

# Multiple permissions (all)
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAllPermissions]
    permissions_required = ['user.create', 'user.delete']

# Single role
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasRole]
    role_required = 'admin'

# Multiple roles (any)
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAnyRole]
    roles_required = ['admin', 'moderator']

# Minimum role level
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [MinimumRoleLevel]
    minimum_role_level = 50  # Manager level

# Owner or has permission
class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrHasPermission]
    permission_required = 'content.update'
    owner_field = 'author'  # Default is 'user'
```

## Default Roles & Levels

| Role | Slug | Level | Description |
|------|------|-------|-------------|
| Guest | `guest` | 0 | Guest user with minimal access |
| User | `user` | 10 | Standard user (default) |
| Premium User | `premium-user` | 20 | Premium subscription user |
| Moderator | `moderator` | 30 | Content moderator |
| Content Manager | `content-manager` | 40 | Manages content and moderators |
| Support Agent | `support-agent` | 50 | Customer support agent |
| Manager | `manager` | 60 | Team manager |
| Admin | `admin` | 70 | Administrator |
| Super Admin | `super-admin` | 80 | Super administrator |

## Default Permissions

### User Management
- `user.view` - View users
- `user.create` - Create users
- `user.update` - Update users
- `user.delete` - Delete users
- `user.list` - List all users
- `user.export` - Export user data
- `user.impersonate` - Impersonate users

### Content Management
- `content.view` - View content
- `content.create` - Create content
- `content.update` - Update content
- `content.delete` - Delete content
- `content.publish` - Publish content
- `content.moderate` - Moderate content

### Analytics
- `analytics.view` - View analytics
- `analytics.export` - Export analytics
- `analytics.dashboard` - Access analytics dashboard

### Settings
- `settings.view` - View settings
- `settings.update` - Update settings
- `settings.system` - Manage system settings

### Billing
- `billing.view` - View billing information
- `billing.manage` - Manage billing
- `billing.invoices` - Access invoices

### Support
- `support.view` - View support tickets
- `support.respond` - Respond to support tickets
- `support.manage` - Manage support system

### API Access
- `api.read` - Read API access
- `api.write` - Write API access
- `api.admin` - Admin API access

### Administration
- `admin.access` - Access admin panel
- `admin.users` - Manage users in admin
- `admin.roles` - Manage roles and permissions
- `admin.logs` - View system logs
- `admin.system` - System administration

## API Endpoints Quick Reference

```bash
# Get current user's permissions
GET /api/rbac/me/permissions/

# Check if user has permission
POST /api/rbac/me/check_permission/
Body: {"permission": "user.create"}

# Check if user has role
POST /api/rbac/me/check_role/
Body: {"role": "admin"}

# List all permissions
GET /api/rbac/permissions/

# List permissions by category
GET /api/rbac/permissions/by_category/

# List all roles
GET /api/rbac/roles/

# Get role hierarchy
GET /api/rbac/roles/hierarchy/

# Get role details
GET /api/rbac/roles/{slug}/

# Get role permissions
GET /api/rbac/roles/{slug}/permissions/

# Get users with role
GET /api/rbac/roles/{slug}/users/

# Create role
POST /api/rbac/roles/
Body: {
  "name": "Custom Role",
  "slug": "custom-role",
  "description": "My custom role",
  "role_type": "custom",
  "level": 45,
  "permission_ids": [1, 2, 3]
}

# Assign role to user
POST /api/rbac/user-roles/
Body: {
  "user": 123,
  "role_id": 3,
  "is_primary": true,
  "expires_at": null
}

# Get user's roles
GET /api/rbac/user-roles/?user_id=123

# Revoke role
POST /api/rbac/user-roles/{id}/revoke/

# Set role as primary
POST /api/rbac/user-roles/{id}/set_primary/

# Get role history
GET /api/rbac/history/?user_id=123
```

## Management Commands

```bash
# Seed RBAC system (roles, permissions, assignments)
python manage.py seed_rbac

# Create superuser
python manage.py createsuperuser

# Check migrations
python manage.py showmigrations rbac accounts
```

## Common Patterns

### Check permission in template

```django
{% if request.user.has_permission('user.create') %}
  <button>Create User</button>
{% endif %}
```

### Check permission in API serializer

```python
class MySerializer(serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()
    
    def get_can_edit(self, obj):
        user = self.context['request'].user
        return user.has_permission('content.update')
```

### Dynamic permission check

```python
# In view
permission_name = f"{resource}.{action}"
if request.user.has_permission(permission_name):
    # Perform action
    pass
```

### Batch assign roles

```python
from apps.rbac.models import Role
from apps.accounts.models import CustomUser

role = Role.objects.get(slug='premium-user')
users = CustomUser.objects.filter(is_premium=True)

for user in users:
    user.assign_role(role, assigned_by=admin_user)
```

### Get users with specific permission

```python
from apps.rbac.models import Permission, UserRole

permission = Permission.objects.get(name='admin.access')
roles_with_permission = permission.roles.filter(is_active=True)
user_roles = UserRole.objects.filter(
    role__in=roles_with_permission,
    is_active=True
)
admin_users = [ur.user for ur in user_roles]
```

## Troubleshooting Commands

```python
# Check user's permissions
user = CustomUser.objects.get(email='user@example.com')
print(user.get_all_permissions().values_list('name', flat=True))

# Check user's roles
print(user.get_active_roles().values_list('role__name', flat=True))

# Check if permission exists
Permission.objects.filter(name='user.create').exists()

# Check role inheritance
role = Role.objects.get(slug='admin')
print(role.get_all_permissions().count())  # Includes inherited

# Find expired roles
from django.utils import timezone
UserRole.objects.filter(expires_at__lt=timezone.now(), is_active=True)

# Role history for user
RoleHistory.objects.filter(user=user).order_by('-created_at')
```

## Settings Configuration

```python
# base.py
AUTH_USER_MODEL = 'accounts.CustomUser'

INSTALLED_APPS = [
    # ...
    'apps.accounts',
    'apps.rbac',
]

MIDDLEWARE = [
    # ... other middleware
    'apps.rbac.middleware.RBACMiddleware',
    'apps.rbac.middleware.RoleExpirationMiddleware',
]

# Optional: URL-based permissions
RBAC_URL_PERMISSIONS = {
    '/api/admin/': 'admin.access',
    '/api/users/': 'user.view',
    '/api/analytics/': 'analytics.view',
}
```

## Testing

```python
from django.test import TestCase
from apps.accounts.models import CustomUser
from apps.rbac.models import Role, Permission

class RBACTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('test@example.com')
        self.admin_role = Role.objects.get(slug='admin')
        
    def test_assign_role(self):
        self.user.assign_role(self.admin_role)
        self.assertTrue(self.user.has_role('admin'))
    
    def test_check_permission(self):
        self.user.assign_role(self.admin_role)
        self.assertTrue(self.user.has_permission('admin.access'))
    
    def test_role_inheritance(self):
        role = Role.objects.get(slug='content-manager')
        inherited_perms = role.get_all_permissions()
        self.assertGreater(inherited_perms.count(), role.permissions.count())
```
