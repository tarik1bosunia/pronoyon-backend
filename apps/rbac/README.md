# ReplyCompass RBAC System

## 🎯 Overview

A comprehensive Role-Based Access Control (RBAC) system for ReplyCompass that provides granular permission management, role hierarchy, and flexible access control.

## ✨ Features

- **Granular Permissions**: Fine-grained access control with `resource.action` format
- **Role Hierarchy**: Inherit permissions from parent roles
- **Multiple Roles per User**: Users can have multiple roles with different contexts
- **Temporary Roles**: Assign roles with expiration dates
- **Audit Trail**: Complete history of role assignments and changes
- **Flexible API**: REST API for managing roles and permissions
- **Django & DRF Support**: Decorators and permission classes for both
- **Automatic Middleware**: Optional URL-based permission checking
- **Context-Based Access**: Scope roles to specific workspaces or projects

## 📁 Project Structure

```
apps/
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py          # CustomUser model with RBAC methods
│   └── signals.py         # Auto-assign default role to new users
└── rbac/
    ├── __init__.py
    ├── admin.py           # Django admin interface
    ├── apps.py
    ├── models.py          # Permission, Role, UserRole, RoleHistory
    ├── permissions.py     # DRF permission classes
    ├── decorators.py      # Django view decorators
    ├── middleware.py      # RBAC & role expiration middleware
    ├── signals.py         # Role change logging
    ├── serializers.py     # DRF serializers
    ├── views.py           # API ViewSets
    ├── urls.py            # API routing
    └── management/
        └── commands/
            └── seed_rbac.py  # Seed command
```

## 🚀 Quick Start

### 1. Installation

The RBAC system is already integrated into ReplyCompass. Just run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Seed Initial Data

Create default roles and permissions:

```bash
python manage.py seed_rbac
```

This creates:
- **9 system roles** (Guest to Super Admin)
- **35+ permissions** across 8 categories
- **Pre-configured permission assignments**

### 3. Create a Superuser

```bash
python manage.py createsuperuser
```

### 4. Access Admin Panel

Visit `http://localhost:8000/admin/` to manage:
- Permissions
- Roles
- User Role Assignments
- Role History

## 📚 Documentation

- **[RBAC Guide](./RBAC_GUIDE.md)**: Complete guide with examples and best practices
- **[Quick Reference](./RBAC_QUICK_REFERENCE.md)**: Cheat sheet for common operations

## 🔑 Default Roles

| Level | Role | Default | Description |
|-------|------|---------|-------------|
| 0 | Guest | ❌ | Minimal access |
| 10 | User | ✅ | Standard user (default) |
| 20 | Premium User | ❌ | Premium features |
| 30 | Moderator | ❌ | Content moderation |
| 40 | Content Manager | ❌ | Manage content |
| 50 | Support Agent | ❌ | Customer support |
| 60 | Manager | ❌ | Team management |
| 70 | Admin | ❌ | Administration |
| 80 | Super Admin | ❌ | Full access |

## 💡 Usage Examples

### Check Permission

```python
# In Django view
if request.user.has_permission('user.create'):
    # Create user
    pass

# With decorator
@permission_required('user.create')
def create_user(request):
    pass

# In DRF ViewSet
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [HasPermission]
    permission_required = 'user.create'
```

### Assign Role

```python
from apps.rbac.models import Role

# Assign role
role = Role.objects.get(slug='moderator')
user.assign_role(role, assigned_by=admin_user)

# Assign with expiration
from datetime import timedelta
from django.utils import timezone

user.assign_role(
    role='premium-user',
    expires_at=timezone.now() + timedelta(days=30)
)
```

### API Usage

```bash
# Get current user's permissions
GET /api/rbac/me/permissions/

# Check permission
POST /api/rbac/me/check_permission/
{"permission": "user.create"}

# Assign role
POST /api/rbac/user-roles/
{
  "user": 123,
  "role_id": 3,
  "is_primary": true
}
```

## 🎨 Permission Categories

- **user**: User Management
- **content**: Content Management
- **analytics**: Analytics & Reports
- **settings**: Settings & Configuration
- **billing**: Billing & Payments
- **support**: Customer Support
- **api**: API Access
- **admin**: Administration

## 🔧 Configuration

### Settings (base.py)

```python
# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Add to INSTALLED_APPS
LOCAL_APPS = [
    'apps.accounts',
    'apps.rbac',
]

# Add middleware
MIDDLEWARE = [
    # ...
    'apps.rbac.middleware.RBACMiddleware',
    'apps.rbac.middleware.RoleExpirationMiddleware',
]

# Optional: URL-based permissions
RBAC_URL_PERMISSIONS = {
    '/api/admin/': 'admin.access',
    '/api/analytics/': 'analytics.view',
}
```

## 🧪 Testing

```python
from django.test import TestCase
from apps.accounts.models import CustomUser
from apps.rbac.models import Role

class RBACTestCase(TestCase):
    def test_user_permission(self):
        user = CustomUser.objects.create_user('test@example.com')
        role = Role.objects.get(slug='user')
        user.assign_role(role)
        
        self.assertTrue(user.has_permission('content.view'))
        self.assertFalse(user.has_permission('admin.access'))
```

## 📊 Models

### Permission
- `name`: Permission identifier (e.g., 'user.create')
- `codename`: URL-safe code
- `description`: Human-readable description
- `category`: Permission category
- `is_active`: Active status

### Role
- `name`: Role name
- `slug`: URL-safe identifier
- `level`: Hierarchy level (0-90)
- `permissions`: ManyToMany with Permission
- `inherits_from`: Parent role for inheritance
- `is_default`: Auto-assign to new users
- `max_users`: Optional user limit

### UserRole
- `user`: ForeignKey to CustomUser
- `role`: ForeignKey to Role
- `is_active`: Active status
- `is_primary`: Primary role flag
- `assigned_by`: Who assigned the role
- `expires_at`: Optional expiration date
- `context`: JSON field for context (workspace_id, etc.)

### RoleHistory
- Complete audit trail of role changes
- Tracks assignments, revocations, and modifications

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rbac/permissions/` | List all permissions |
| GET | `/api/rbac/permissions/by_category/` | Permissions by category |
| GET | `/api/rbac/roles/` | List all roles |
| GET | `/api/rbac/roles/{slug}/` | Role details |
| GET | `/api/rbac/roles/{slug}/permissions/` | Role permissions |
| GET | `/api/rbac/roles/hierarchy/` | Role hierarchy |
| POST | `/api/rbac/user-roles/` | Assign role to user |
| POST | `/api/rbac/user-roles/{id}/revoke/` | Revoke role |
| GET | `/api/rbac/me/permissions/` | Current user permissions |
| POST | `/api/rbac/me/check_permission/` | Check permission |
| GET | `/api/rbac/history/` | Role history |

## 🎯 Best Practices

1. **Use Permissions Over Roles**: Check for specific capabilities
2. **Follow Naming Convention**: `resource.action` format
3. **Leverage Inheritance**: Don't duplicate permissions
4. **Regular Audits**: Review role assignments periodically
5. **Context-Based Roles**: Use context for workspace-specific access
6. **Set Expiration**: Use temporary roles for trial periods

## 🐛 Troubleshooting

### Permission not working?
1. Check if user is authenticated
2. Verify role is active: `user.get_active_roles()`
3. Check permission exists: `Permission.objects.filter(name='...')`
4. Verify not expired: `user_role.is_expired()`

### Role not inheriting?
1. Check `inherits_from` is set
2. Ensure parent role is active
3. Use `role.get_all_permissions()` to verify

### Can't access admin?
1. Assign 'admin' role or higher
2. Check `is_staff=True` for Django admin access
3. Verify `admin.access` permission

## 📄 License

Part of ReplyCompass project.

## 🤝 Contributing

1. Follow existing code patterns
2. Add tests for new features
3. Update documentation
4. Create permission names following convention

---

**Need Help?** Check the [RBAC Guide](./RBAC_GUIDE.md) for detailed documentation.
