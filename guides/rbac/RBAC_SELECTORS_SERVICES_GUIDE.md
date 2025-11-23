# Selectors and Services Architecture Guide

## Overview

The RBAC system now follows the **Selectors and Services** pattern for better code organization, maintainability, and testability. This architecture separates concerns into distinct layers:

- **Selectors**: Data access layer (queries)
- **Services**: Business logic layer (operations)
- **Models**: Data layer (structure)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        API / Views                          │
│              (controllers, viewsets, decorators)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├──► Read Operations
                     │    └──► Selectors
                     │         ├─► PermissionSelectors
                     │         ├─► RoleSelectors
                     │         ├─► UserRoleSelectors
                     │         └─► RoleHistorySelectors
                     │
                     └──► Write Operations
                          └──► Services
                               ├─► PermissionService
                               ├─► RoleService
                               ├─► UserRoleService
                               ├─► PermissionCheckService
                               └─► RoleAnalyticsService
                               
┌─────────────────────────────────────────────────────────────┐
│                      Selectors Layer                        │
│             (Pure data retrieval functions)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      Services Layer                         │
│         (Business logic, validations, transactions)         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      Models Layer                           │
│              (Database structure & ORM)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Selectors (Data Access Layer)

### Purpose
Selectors are **pure functions** that retrieve data from the database. They:
- ✅ Have NO side effects
- ✅ Only perform SELECT queries
- ✅ Return QuerySets or model instances
- ✅ Can be cached
- ✅ Are easily testable

### File: `apps/rbac/selectors.py`

### Classes

#### 1. PermissionSelectors

Handles all permission-related queries.

**Methods:**
```python
# Get all permissions
get_all_permissions() -> QuerySet

# Get single permission
get_permission_by_name(name: str) -> Optional[Permission]
get_permission_by_codename(codename: str) -> Optional[Permission]

# Filter permissions
get_permissions_by_category(category: str) -> QuerySet
get_permissions_by_names(names: List[str]) -> QuerySet

# Grouped/organized data
get_permissions_grouped_by_category() -> dict

# Search
search_permissions(query: str) -> QuerySet
```

**Usage Example:**
```python
from apps.rbac.selectors import PermissionSelectors

# Get all active permissions
permissions = PermissionSelectors.get_all_permissions()

# Get specific permission
perm = PermissionSelectors.get_permission_by_name('user.create')

# Get permissions by category
user_perms = PermissionSelectors.get_permissions_by_category('user')

# Search permissions
results = PermissionSelectors.search_permissions('admin')
```

#### 2. RoleSelectors

Handles all role-related queries.

**Methods:**
```python
# Get all roles
get_all_roles() -> QuerySet

# Get single role
get_role_by_slug(slug: str) -> Optional[Role]
get_role_by_name(name: str) -> Optional[Role]

# Filter roles
get_roles_by_level(min_level: int, max_level: int) -> QuerySet
get_roles_by_type(role_type: str) -> QuerySet

# Special roles
get_default_role() -> Optional[Role]

# Hierarchy
get_role_hierarchy() -> QuerySet
get_roles_inheriting_from(role: Role) -> QuerySet

# Assignment checks
get_assignable_roles(max_level: Optional[int]) -> QuerySet
```

**Usage Example:**
```python
from apps.rbac.selectors import RoleSelectors

# Get role by slug
admin_role = RoleSelectors.get_role_by_slug('admin')

# Get default role for new users
default_role = RoleSelectors.get_default_role()

# Get role hierarchy
hierarchy = RoleSelectors.get_role_hierarchy()

# Get roles by level range
management_roles = RoleSelectors.get_roles_by_level(50, 70)
```

#### 3. UserRoleSelectors

Handles user-role assignment queries.

**Methods:**
```python
# User's roles
get_user_active_roles(user) -> QuerySet
get_user_primary_role(user) -> Optional[UserRole]
get_user_roles_by_context(user, context: dict) -> QuerySet

# Role's users
get_users_with_role(role: Role) -> QuerySet
get_users_with_permission(permission_name: str) -> QuerySet

# Expired roles
get_expired_user_roles() -> QuerySet

# Single assignment
get_user_role_by_id(user_role_id: int) -> Optional[UserRole]

# Checks
user_has_role(user, role_slug: str) -> bool

# Permissions
get_user_permissions(user) -> QuerySet
```

**Usage Example:**
```python
from apps.rbac.selectors import UserRoleSelectors

# Get user's active roles
user_roles = UserRoleSelectors.get_user_active_roles(user)

# Get primary role
primary = UserRoleSelectors.get_user_primary_role(user)

# Get all users with admin role
admin_users = UserRoleSelectors.get_users_with_role(admin_role)

# Get user's permissions
permissions = UserRoleSelectors.get_user_permissions(user)

# Check if user has role
has_admin = UserRoleSelectors.user_has_role(user, 'admin')
```

#### 4. RoleHistorySelectors

Handles role history queries.

**Methods:**
```python
# User history
get_user_role_history(user, limit: Optional[int]) -> QuerySet

# Filter by action
get_role_history_by_action(action: str) -> QuerySet

# Recent changes
get_recent_role_changes(days: int = 7) -> QuerySet

# Performer tracking
get_role_assignments_by_performer(performer) -> QuerySet
```

**Usage Example:**
```python
from apps.rbac.selectors import RoleHistorySelectors

# Get user's role history
history = RoleHistorySelectors.get_user_role_history(user, limit=10)

# Get recent role changes
recent = RoleHistorySelectors.get_recent_role_changes(days=30)

# Get assignments by admin
assignments = RoleHistorySelectors.get_role_assignments_by_performer(admin)
```

---

## Services (Business Logic Layer)

### Purpose
Services handle business logic, validations, and database modifications. They:
- ✅ Contain business rules
- ✅ Perform CREATE, UPDATE, DELETE operations
- ✅ Use transactions
- ✅ Validate data
- ✅ Orchestrate complex operations
- ✅ Call selectors for data retrieval

### File: `apps/rbac/services.py`

### Classes

#### 1. PermissionService

Handles permission creation and modification.

**Methods:**
```python
# Create
create_permission(name, codename, description, category, is_active) -> Permission

# Update
update_permission(permission, **kwargs) -> Permission

# Deactivate
deactivate_permission(permission) -> Permission

# Bulk operations
bulk_create_permissions(permissions_data) -> List[Permission]
```

**Usage Example:**
```python
from apps.rbac.services import PermissionService

# Create permission
permission = PermissionService.create_permission(
    name='invoice.export',
    codename='invoice-export',
    description='Export invoices to PDF',
    category='billing'
)

# Update permission
PermissionService.update_permission(
    permission,
    description='Updated description'
)

# Bulk create
permissions = PermissionService.bulk_create_permissions([
    {'name': 'report.view', 'codename': 'report-view', 'category': 'analytics'},
    {'name': 'report.export', 'codename': 'report-export', 'category': 'analytics'},
])
```

#### 2. RoleService

Handles role creation, modification, and permissions assignment.

**Methods:**
```python
# Create
create_role(name, slug, description, role_type, level, ...) -> Role

# Update
update_role(role, permission_ids, **kwargs) -> Role

# Permissions
add_permissions_to_role(role, permission_ids) -> Role
remove_permissions_from_role(role, permission_ids) -> Role

# Deactivate
deactivate_role(role) -> Role

# Helpers
get_role_effective_permissions(role) -> List[Permission]
check_role_can_accept_users(role) -> bool
```

**Usage Example:**
```python
from apps.rbac.services import RoleService

# Create role
role = RoleService.create_role(
    name='Project Manager',
    slug='project-manager',
    description='Manages projects',
    level=55,
    permission_ids=[1, 2, 3, 5]
)

# Add permissions
RoleService.add_permissions_to_role(role, [7, 8, 9])

# Update role
RoleService.update_role(
    role,
    description='Updated description',
    level=60
)

# Get effective permissions (including inherited)
permissions = RoleService.get_role_effective_permissions(role)
```

#### 3. UserRoleService

Handles user-role assignments and management.

**Methods:**
```python
# Assign
assign_role_to_user(user, role, assigned_by, expires_at, context, is_primary, notes) -> UserRole

# Revoke
revoke_role_from_user(user, role) -> bool

# Primary role
set_primary_role(user_role) -> UserRole

# Expiration
extend_role_expiration(user_role, new_expiration) -> UserRole

# Bulk operations
bulk_assign_role(users, role, assigned_by, expires_at) -> List[UserRole]

# Maintenance
expire_user_roles() -> int
```

**Usage Example:**
```python
from apps.rbac.services import UserRoleService
from datetime import timedelta
from django.utils import timezone

# Assign role
user_role = UserRoleService.assign_role_to_user(
    user=user,
    role=admin_role,
    assigned_by=current_user,
    expires_at=timezone.now() + timedelta(days=30),
    is_primary=True
)

# Revoke role
UserRoleService.revoke_role_from_user(user, 'moderator')

# Set as primary
UserRoleService.set_primary_role(user_role)

# Bulk assign
UserRoleService.bulk_assign_role(
    users=[user1, user2, user3],
    role=premium_role,
    assigned_by=admin
)

# Expire roles (maintenance task)
expired_count = UserRoleService.expire_user_roles()
```

#### 4. PermissionCheckService

Handles permission checking logic.

**Methods:**
```python
# Permission checks
user_has_permission(user, permission_name) -> bool
user_has_any_permission(user, permission_names) -> bool
user_has_all_permissions(user, permission_names) -> bool

# Role checks
user_has_role(user, role_identifier) -> bool

# Level checks
get_user_role_level(user) -> int
user_meets_minimum_level(user, minimum_level) -> bool
```

**Usage Example:**
```python
from apps.rbac.services import PermissionCheckService

# Check permission
if PermissionCheckService.user_has_permission(user, 'user.create'):
    # User can create users
    pass

# Check any permission
if PermissionCheckService.user_has_any_permission(user, ['admin.access', 'admin.users']):
    # User has admin access
    pass

# Check role level
if PermissionCheckService.user_meets_minimum_level(user, 50):
    # User is manager level or higher
    pass

# Get user level
level = PermissionCheckService.get_user_role_level(user)
```

#### 5. RoleAnalyticsService

Provides analytics and reporting.

**Methods:**
```python
# Distribution
get_role_distribution() -> Dict[str, int]

# Usage
get_permission_usage() -> Dict[str, int]

# User summary
get_user_role_summary(user) -> Dict[str, Any]
```

**Usage Example:**
```python
from apps.rbac.services import RoleAnalyticsService

# Get role distribution
distribution = RoleAnalyticsService.get_role_distribution()
# {'Admin': 5, 'User': 120, 'Moderator': 15}

# Get permission usage
usage = RoleAnalyticsService.get_permission_usage()
# {'user.view': 140, 'admin.access': 5}

# Get user summary
summary = RoleAnalyticsService.get_user_role_summary(user)
# {
#   'user': <User>,
#   'roles': [<UserRole>, ...],
#   'primary_role': <Role>,
#   'role_count': 2,
#   'permissions': [<Permission>, ...],
#   'permission_count': 15,
#   'role_level': 50
# }
```

---

## Usage Patterns

### Pattern 1: Read Data (Use Selectors)

```python
# ❌ DON'T: Query directly in views
def my_view(request):
    permissions = Permission.objects.filter(is_active=True, category='user')

# ✅ DO: Use selectors
from apps.rbac.selectors import PermissionSelectors

def my_view(request):
    permissions = PermissionSelectors.get_permissions_by_category('user')
```

### Pattern 2: Modify Data (Use Services)

```python
# ❌ DON'T: Create/modify directly in views
def assign_role_view(request):
    user_role = UserRole.objects.create(
        user=user,
        role=role,
        assigned_by=request.user
    )

# ✅ DO: Use services
from apps.rbac.services import UserRoleService

def assign_role_view(request):
    user_role = UserRoleService.assign_role_to_user(
        user=user,
        role=role,
        assigned_by=request.user
    )
```

### Pattern 3: Permission Checks (Use Service)

```python
# ❌ DON'T: Inline permission logic
def my_view(request):
    if request.user.is_superuser or request.user.get_all_permissions().filter(name='user.create').exists():
        # Logic

# ✅ DO: Use permission check service
from apps.rbac.services import PermissionCheckService

def my_view(request):
    if PermissionCheckService.user_has_permission(request.user, 'user.create'):
        # Logic
```

### Pattern 4: Complex Operations (Combine Selectors + Services)

```python
from apps.rbac.selectors import RoleSelectors, UserRoleSelectors
from apps.rbac.services import UserRoleService

def promote_users_to_manager(min_level=30):
    """Promote all users with level >= 30 to manager"""
    
    # Use selector to get data
    manager_role = RoleSelectors.get_role_by_slug('manager')
    users_to_promote = UserRoleSelectors.get_users_with_role_level_min(min_level)
    
    # Use service to perform operation
    UserRoleService.bulk_assign_role(
        users=users_to_promote,
        role=manager_role,
        assigned_by=admin_user
    )
```

---

## Benefits of This Architecture

### 1. Separation of Concerns
- **Selectors**: Only read data
- **Services**: Only business logic
- **Views**: Only presentation/coordination

### 2. Reusability
```python
# Use same selector in multiple places
permissions = PermissionSelectors.get_all_permissions()  # View
permissions = PermissionSelectors.get_all_permissions()  # API
permissions = PermissionSelectors.get_all_permissions()  # Management command
```

### 3. Testability
```python
# Easy to test selectors (no side effects)
def test_get_permissions_by_category():
    perms = PermissionSelectors.get_permissions_by_category('user')
    assert perms.count() > 0

# Easy to test services (mock selectors)
@patch('apps.rbac.selectors.RoleSelectors.get_role_by_slug')
def test_assign_role(mock_selector):
    mock_selector.return_value = mock_role
    result = UserRoleService.assign_role_to_user(user, mock_role)
    assert result.is_active
```

### 4. Maintainability
- Changes to queries only affect selectors
- Changes to business logic only affect services
- Clear responsibilities for each layer

### 5. Performance
- Selectors can be optimized independently
- Easy to add caching to selectors
- Transactions handled by services

---

## File Structure

```
apps/rbac/
├── models.py          # Data models
├── selectors.py       # Data access layer (NEW)
├── services.py        # Business logic layer (NEW)
├── views.py           # API views (use selectors + services)
├── permissions.py     # DRF permissions (use services)
├── decorators.py      # View decorators (use services)
├── middleware.py      # Middleware (use services)
└── admin.py          # Admin interface (use selectors)
```

---

## Migration Guide

### Updating Existing Code

**Before:**
```python
# views.py
permissions = Permission.objects.filter(category='user', is_active=True)
role = Role.objects.get(slug='admin')
user_role = UserRole.objects.create(user=user, role=role)
```

**After:**
```python
# views.py
from apps.rbac.selectors import PermissionSelectors, RoleSelectors
from apps.rbac.services import UserRoleService

permissions = PermissionSelectors.get_permissions_by_category('user')
role = RoleSelectors.get_role_by_slug('admin')
user_role = UserRoleService.assign_role_to_user(user, role)
```

---

## Best Practices

### DO ✅
- Use selectors for all read operations
- Use services for all write operations
- Keep selectors pure (no side effects)
- Use transactions in services
- Validate data in services
- Return QuerySets from selectors (for chaining)

### DON'T ❌
- Don't query models directly in views
- Don't create/update objects directly in views
- Don't put business logic in selectors
- Don't perform queries in services (use selectors)
- Don't mix layers

---

## Quick Reference

| Task | Use | Example |
|------|-----|---------|
| Get data | Selector | `PermissionSelectors.get_all_permissions()` |
| Create data | Service | `PermissionService.create_permission(...)` |
| Update data | Service | `RoleService.update_role(...)` |
| Delete data | Service | `UserRoleService.revoke_role_from_user(...)` |
| Check permission | Service | `PermissionCheckService.user_has_permission(...)` |
| Analytics | Service | `RoleAnalyticsService.get_role_distribution()` |

---

**The selectors and services pattern provides a clean, maintainable, and testable architecture for your RBAC system!** 🎉
