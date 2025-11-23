# Multiple Frontend Support - Configuration Guide

## Overview

The ReplyCompass backend now supports **multiple frontend applications** accessing the same API. This is perfect for:

- User-facing application
- Admin dashboard
- Mobile web application
- Partner portals
- Different frontend frameworks/ports

---

## Configuration Variables

### Two Frontend Variables

#### 1. **FRONTEND_URL** (Single/Primary)
```env
FRONTEND_URL=http://localhost:3000
```
- **Purpose:** Default/primary frontend
- **Used for:** Email links, OAuth callbacks, default redirects
- **Required:** Yes

#### 2. **FRONTEND_URLS** (Multiple)
```env
FRONTEND_URLS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```
- **Purpose:** All frontend applications
- **Used for:** Validation, multi-app support, callbacks
- **Format:** Comma-separated list
- **Required:** Yes (defaults to FRONTEND_URL if not set)

---

## Settings Configuration

In `config/settings/base.py`:

```python
# Single primary frontend
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# Multiple frontends
FRONTEND_URLS = config('FRONTEND_URLS', default='http://localhost:3000', cast=Csv())
```

### Behavior:
- If only `FRONTEND_URL` is set → single frontend
- If `FRONTEND_URLS` is set → multiple frontends
- `FRONTEND_URL` is always the primary/default

---

## Environment Examples

### Development - Single Frontend
```env
# Single React app
FRONTEND_URL=http://localhost:3000
FRONTEND_URLS=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Development - Multiple Frontends
```env
# User app (primary)
FRONTEND_URL=http://localhost:3000

# All apps (user + admin + mobile)
FRONTEND_URLS=http://localhost:3000,http://localhost:3001,http://localhost:5173

# CORS for all apps
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173,http://127.0.0.1:3000
```

### Production - Multiple Domains
```env
# Primary user app
FRONTEND_URL=https://app.replycompass.com

# All apps
FRONTEND_URLS=https://app.replycompass.com,https://admin.replycompass.com,https://mobile.replycompass.com

# CORS
CORS_ALLOWED_ORIGINS=https://app.replycompass.com,https://admin.replycompass.com,https://mobile.replycompass.com
```

---

## Usage in Code

### Using the Utility Functions

#### Get Primary Frontend URL
```python
from apps.core.frontend_utils import get_primary_frontend_url

# Get default frontend URL
url = get_primary_frontend_url()
# Returns: 'http://localhost:3000'
```

#### Get All Frontend URLs
```python
from apps.core.frontend_utils import get_all_frontend_urls

# Get list of all frontends
urls = get_all_frontend_urls()
# Returns: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:5173']
```

#### Validate Frontend URL
```python
from apps.core.frontend_utils import is_valid_frontend_url

# Check if URL is allowed
if is_valid_frontend_url('http://localhost:3001'):
    # Allow access
    pass
```

#### Generate Redirect URLs
```python
from apps.core.frontend_utils import get_frontend_redirect_url

# Generate URL with path
reset_url = get_frontend_redirect_url('/reset-password/abc123')
# Returns: 'http://localhost:3000/reset-password/abc123'

# Use specific frontend
admin_url = get_frontend_redirect_url('/dashboard', 'http://localhost:3001')
# Returns: 'http://localhost:3001/dashboard'
```

#### Get Frontend by Type
```python
from apps.core.frontend_utils import get_frontend_url_by_type

# Get admin panel URL
admin_url = get_frontend_url_by_type('admin')
# Returns: 'http://localhost:3001'

# Get mobile app URL
mobile_url = get_frontend_url_by_type('mobile')
# Returns: 'http://localhost:5173'
```

#### Generate Email Links
```python
from apps.core.frontend_utils import generate_email_verification_url, generate_password_reset_url

# For regular users
user_verify_url = generate_email_verification_url('token123', user_type='user')
# Returns: 'http://localhost:3000/verify-email/token123'

# For admin users
admin_verify_url = generate_email_verification_url('token456', user_type='admin')
# Returns: 'http://localhost:3001/verify-email/token456'

# Password reset
reset_url = generate_password_reset_url('reset_token', user_type='user')
# Returns: 'http://localhost:3000/reset-password/reset_token'
```

#### OAuth Redirects
```python
from apps.core.frontend_utils import get_oauth_redirect_url

# Google OAuth for users
user_callback = get_oauth_redirect_url('google', user_type='user')
# Returns: 'http://localhost:3000/auth/google/callback'

# Google OAuth for admins
admin_callback = get_oauth_redirect_url('google', user_type='admin')
# Returns: 'http://localhost:3001/auth/google/callback'
```

---

## Real-World Use Cases

### Use Case 1: Email Verification
```python
# views.py
from apps.core.frontend_utils import generate_email_verification_url
from django.core.mail import send_mail

def send_verification_email(user, token):
    # Determine user type
    user_type = 'admin' if user.is_staff else 'user'
    
    # Generate appropriate URL
    verify_url = generate_email_verification_url(token, user_type)
    
    send_mail(
        'Verify your email',
        f'Click here to verify: {verify_url}',
        'noreply@replycompass.com',
        [user.email],
    )
```

### Use Case 2: OAuth Redirect
```python
# views.py
from apps.core.frontend_utils import get_oauth_redirect_url

def google_oauth_view(request):
    # Check if admin or user
    is_admin = request.GET.get('admin') == 'true'
    user_type = 'admin' if is_admin else 'user'
    
    # Get appropriate callback URL
    redirect_uri = get_oauth_redirect_url('google', user_type)
    
    # Continue with OAuth flow...
```

### Use Case 3: API Response with Multiple URLs
```python
# serializers.py or views.py
from apps.core.frontend_utils import get_all_frontend_urls

def get_app_info(request):
    return Response({
        'available_apps': [
            {
                'name': 'User Dashboard',
                'url': get_frontend_url_by_type('user'),
                'type': 'user'
            },
            {
                'name': 'Admin Panel',
                'url': get_frontend_url_by_type('admin'),
                'type': 'admin'
            },
            {
                'name': 'Mobile App',
                'url': get_frontend_url_by_type('mobile'),
                'type': 'mobile'
            },
        ]
    })
```

### Use Case 4: Redirect After Login
```python
# views.py
from apps.core.frontend_utils import get_frontend_url_by_type, get_frontend_redirect_url

def redirect_after_login(user):
    # Determine where to redirect based on user role
    if user.is_superuser or user.is_staff:
        # Redirect to admin panel
        return get_frontend_redirect_url('/dashboard', get_frontend_url_by_type('admin'))
    elif user.role == 'partner':
        # Redirect to partner portal
        return get_frontend_redirect_url('/partner-dashboard', get_frontend_url_by_type('partner'))
    else:
        # Regular user - main app
        return get_frontend_redirect_url('/home')
```

---

## Application Type Mapping

The utility functions support these app types by default:

| App Type | Description | URL Index | Example |
|----------|-------------|-----------|---------|
| `user` | Primary user app | FRONTEND_URL (default) | User dashboard |
| `admin` | Admin panel | FRONTEND_URLS[1] | Admin interface |
| `mobile` | Mobile web app | FRONTEND_URLS[2] | Mobile optimized |
| `partner` | Partner portal | FRONTEND_URLS[3] | Partner dashboard |

**Configuration Example:**
```env
FRONTEND_URL=http://localhost:3000                    # user (default)
FRONTEND_URLS=http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8080
              # Index 0: user           ^            ^                     ^
              # Index 1: admin          └────────────┘                     │
              # Index 2: mobile                                            │
              # Index 3: partner                                           └──────────────┘
```

---

## Benefits of Multiple Frontend Support

✅ **Separation of Concerns**
- Different apps for different user types
- Cleaner codebase per frontend

✅ **Better User Experience**
- Optimized interfaces for each user role
- Admin tools separate from user interface

✅ **Flexibility**
- Different frameworks per frontend
- Independent deployment
- A/B testing different frontends

✅ **Security**
- Admin panel on different domain
- Easier to apply different security policies

✅ **Scalability**
- Scale frontends independently
- Add new frontends without backend changes

---

## Migration from Single to Multiple Frontends

### Before (Single Frontend)
```env
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### After (Multiple Frontends)
```env
FRONTEND_URL=http://localhost:3000
FRONTEND_URLS=http://localhost:3000,http://localhost:3001
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Backward Compatible:** Existing code using `settings.FRONTEND_URL` continues to work!

---

## Summary

✅ **Two Variables:**
- `FRONTEND_URL` - Primary frontend (required)
- `FRONTEND_URLS` - All frontends (optional, defaults to FRONTEND_URL)

✅ **Utility Functions Available:**
- Get primary/all frontend URLs
- Validate frontend URLs
- Generate redirect URLs
- Type-based URL selection
- Email/OAuth URL generation

✅ **Backward Compatible:**
- Single frontend still works
- No breaking changes

✅ **Production Ready:**
- Environment-based configuration
- Supports multiple domains
- CORS properly configured

**Your backend is now ready to support multiple frontend applications!** 🚀
