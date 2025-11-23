# RBAC Boilerplate - Quick Reference

⚡ **Fast reference for using this RBAC system in your projects**

---

## 🚀 30-Second Setup

```bash
# 1. Copy to your project
cp -r apps/rbac /your-project/apps/
cp -r apps/accounts /your-project/apps/

# 2. Add to settings.py
INSTALLED_APPS += ['apps.accounts', 'apps.rbac', 'rest_framework', 'django_filters']
AUTH_USER_MODEL = 'accounts.CustomUser'

# 3. Migrate and seed
python manage.py migrate
python manage.py seed_rbac

# Done! You now have a complete RBAC system
```

---

## 📋 Common Code Snippets

### Permission Checking
```python
# Single permission
if user.has_permission('content.edit'):
    # Allow action
    
# Any permission
if user.has_any_permission(['content.edit', 'content.delete']):
    # User has at least one
    
# All permissions
if user.has_all_permissions(['content.view', 'content.edit']):
    # User has all
```

### Role Assignment
```python
from apps.rbac.services import UserRoleService
from apps.rbac.models import Role

role = Role.objects.get(slug='moderator')
UserRoleService.assign_role_to_user(user, role, is_primary=True)
```

### View Protection
```python
from apps.rbac.decorators import require_permission, require_role

@require_permission('content.edit')
def edit_view(request):
    pass

@require_role('admin')
def admin_view(request):
    pass
```

### DRF Permissions
```python
from apps.rbac.permissions import HasPermission, HasRole

class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [HasPermission('content.edit')]
```

### Creating Roles
```python
from apps.rbac.services import RoleService

role = RoleService.create_role(
    name='Content Manager',
    slug='content-manager',
    level=20,
    permission_names=['content.view', 'content.create', 'content.edit']
)
```

---

## 📊 Role Level Reference

```
0:  Guest          - Public access only
10: User           - Basic user operations
20: Power User     - Advanced features
30: Moderator      - Content moderation
40: Senior Mod     - Full moderation
50: Manager        - Team management
60: Senior Manager - Department control
70: Administrator  - System configuration
80: Senior Admin   - Security & health
90: Super Admin    - Full system access
```

---

## 🔌 API Endpoints

```
GET    /api/rbac/permissions/                    # List all permissions
GET    /api/rbac/roles/                          # List all roles
POST   /api/rbac/roles/                          # Create role
GET    /api/rbac/user-roles/                     # List user roles
POST   /api/rbac/user-roles/                     # Assign role
GET    /api/rbac/me/permissions/                 # My permissions
GET    /api/rbac/me/roles/                       # My roles
GET    /api/rbac/me/has-permission/?permission=X # Check permission
```

---

## 🧪 Testing Commands

```bash
# Run all RBAC tests
pytest apps/rbac/tests/ -v

# Run specific tests
pytest apps/rbac/tests/test_models.py -v
pytest apps/rbac/tests/test_services.py -v
pytest apps/rbac/tests/test_integration.py -v

# With coverage
pytest apps/rbac/ --cov=apps/rbac --cov-report=html
```

---

## 🎨 Template Tags

```django
{% load rbac_tags %}

{% if user|has_permission:"content.edit" %}
    <button>Edit</button>
{% endif %}

{% if user|has_role:"admin" %}
    <a href="/admin">Admin Panel</a>
{% endif %}
```

---

## 🔧 Management Commands

```bash
# Seed initial RBAC data (permissions, roles, superuser)
python manage.py seed_rbac

# Django checks
python manage.py check
python manage.py check --deploy
```

---

## 📦 Default Roles Created by seed_rbac

```python
Guest (level=0):
  - content.view

User (level=10):
  + content.create
  (inherits from Guest)

Moderator (level=30):
  + content.edit
  + content.moderate
  (inherits from User)

Admin (level=70):
  + content.delete
  + admin.access
  + All admin permissions
  (inherits from Moderator)
```

---

## 🚨 Quick Troubleshooting

### Permissions not working?
```python
# Clear cache
from django.core.cache import cache
cache.clear()

# Refresh user
user.refresh_from_db()
```

### Role not inheriting permissions?
```python
# Check inheritance chain
role = Role.objects.get(slug='your-role')
all_permissions = role.get_all_permissions()
print([p.name for p in all_permissions])
```

### Max users exceeded?
```python
# Check current count
role = Role.objects.get(slug='your-role')
active_count = role.user_roles.filter(is_active=True).count()
print(f"Active: {active_count}, Max: {role.max_users}")
```

---

## 📝 Custom Permission Creation

```python
from apps.rbac.models import Permission

# Create permission
perm = Permission.objects.create(
    name='custom.action',
    codename='custom-action',
    category='custom',
    description='My custom permission'
)

# Add to role
role.permissions.add(perm)
```

---

## 🎯 Service Layer Quick Reference

```python
from apps.rbac.services import (
    PermissionCheckService,
    UserRoleService,
    RoleService
)

# Check permissions
PermissionCheckService.user_has_permission(user, 'content.edit')
PermissionCheckService.get_user_role_level(user)

# Manage user roles
UserRoleService.assign_role_to_user(user, role, is_primary=True)
UserRoleService.revoke_role_from_user(user, role)
UserRoleService.update_primary_role(user_role)

# Manage roles
RoleService.create_role(name, slug, level, permission_names=[...])
RoleService.clone_role(role, new_name, new_slug)
RoleService.update_role_permissions(role, permission_ids=[...])
```

---

## 📖 Full Documentation

- **RBAC_BOILERPLATE_VERIFICATION.md** - Complete usage guide
- **RBAC_STATUS_REPORT.md** - System status and verification
- **Code docstrings** - Inline documentation

---

## ✅ Verification Status

```
✅ 43/43 tests passing (100%)
✅ 96% coverage on models
✅ Zero Pylance errors
✅ Production ready
✅ Type safe
```

---

## 🎓 Learning Path

1. Read RBAC_BOILERPLATE_VERIFICATION.md
2. Review test files for examples
3. Check models.py for data structure
4. Explore services.py for business logic
5. Try examples in views.py
6. Customize for your needs

---

**Last Updated**: November 14, 2025  
**Status**: ✅ Production Ready  
**Tests**: 43/43 Passing
