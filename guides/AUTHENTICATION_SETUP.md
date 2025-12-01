# Authentication Setup - Email/Password & Google OAuth

**Project**: ReplyCompass  
**Authentication Methods**: Email/Password + Google OAuth  
**Status**: ✅ Configured (Requires Google OAuth Setup)

---

## 🎯 Overview

Your project supports **TWO authentication methods**:

1. ✅ **Email & Password Login** - Fully configured and working
2. ⚠️ **Google OAuth Login** - Configured but requires Google Cloud setup

---

## ✅ Current Configuration Status

### What's Already Configured:

#### 1. Django Allauth (✅ Installed)
```python
INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google provider
]
```

#### 2. dj-rest-auth (✅ Installed)
```python
INSTALLED_APPS = [
    'dj_rest_auth',
    'dj_rest_auth.registration',
]
```

#### 3. Authentication Backend (✅ Configured)
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Email/Password
    'allauth.account.auth_backends.AuthenticationBackend',  # Social + Email
]
```

#### 4. Custom User Model (✅ Configured)
```python
AUTH_USER_MODEL = 'accounts.CustomUser'
# Uses email as username field (no separate username)
```

#### 5. JWT Configuration (✅ Configured)
```python
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': False,
    'JWT_AUTH_COOKIE': 'auth-token',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh-token',
}
```

#### 6. Email/Password Settings (✅ Configured)
```python
ACCOUNT_LOGIN_METHODS = ['email']  # Email-based login
ACCOUNT_EMAIL_VERIFICATION = 'none'  # For development
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # No username, email only
```

#### 7. Social Account Settings (✅ Configured)
```python
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}
```

---

## 📋 API Endpoints Available

### Email/Password Authentication (✅ Working Now)

```bash
# Registration
POST /api/auth/registration/
Body: {
    "email": "user@example.com",
    "password1": "SecurePass123!",
    "password2": "SecurePass123!"
}

# Login
POST /api/auth/login/
Body: {
    "email": "user@example.com",
    "password": "SecurePass123!"
}
Response: {
    "access": "jwt-access-token",
    "refresh": "jwt-refresh-token",
    "user": {...}
}

# Logout
POST /api/auth/logout/
Headers: Authorization: Bearer {access-token}

# Token Refresh
POST /api/auth/token/refresh/
Body: {
    "refresh": "jwt-refresh-token"
}

# Get User Profile
GET /api/auth/user/
Headers: Authorization: Bearer {access-token}

# Update User Profile
PUT/PATCH /api/auth/user/
Headers: Authorization: Bearer {access-token}
Body: {
    "first_name": "John",
    "last_name": "Doe"
}

# Change Password
POST /api/auth/password/change/
Headers: Authorization: Bearer {access-token}
Body: {
    "old_password": "OldPass123!",
    "new_password1": "NewPass123!",
    "new_password2": "NewPass123!"
}

# Password Reset Request
POST /api/auth/password/reset/
Body: {
    "email": "user@example.com"
}

# Password Reset Confirm
POST /api/auth/password/reset/confirm/
Body: {
    "uid": "user-id",
    "token": "reset-token",
    "new_password1": "NewPass123!",
    "new_password2": "NewPass123!"
}
```

### Google OAuth (⚠️ Needs Setup)

```bash
# Exchange a Google OAuth access token for JWTs
POST /api/auth/google/
Body: {
    "auth_token": "google-oauth-access-token"
}

Response:
{
  "access": "jwt-access-token",
  "refresh": "jwt-refresh-token",
  "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "Google",
      "last_name": "User"
  }
}
```

> ℹ️ Generate `auth_token` on the frontend using `@react-oauth/google` (or Google Identity Services). Send the `access_token` returned by Google to this endpoint.

---

## 🔧 Setup Required: Google OAuth

### Current Status:
- ⚠️ **Site Domain**: Currently set to `example.com` (needs update)
- ⚠️ **Google OAuth App**: Not configured in database
- ⚠️ **Google Credentials**: Need to be added to `.env`

### Steps to Enable Google OAuth:

#### Step 1: Update Django Site
```bash
docker compose exec web python manage.py shell

# In Python shell:
from django.contrib.sites.models import Site
site = Site.objects.get_current()
site.domain = 'localhost:8000'  # For development
site.name = 'ReplyCompass'
site.save()
exit()
```

#### Step 2: Create Google OAuth App

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create/Select Project**
   - Create a new project or select existing one
   - Name: "ReplyCompass" (or your preferred name)

3. **Enable Google+ API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: "ReplyCompass Web"
   
5. **Configure OAuth Consent Screen**
   - User Type: "External" (for development)
   - App name: "ReplyCompass"
   - User support email: your-email@example.com
   - Developer contact: your-email@example.com
   - Add scopes: `email`, `profile`, `openid`

6. **Add Authorized JavaScript Origins** (required for the popup/token flow)
  ```
  Development:
  http://localhost:3000
  http://localhost:8000  # Optional API origin if you open the popup from backend domain
   
  Production:
  https://yourdomain.com
  https://app.yourdomain.com (if you have multiple frontends)
  ```

7. **(Optional) Add Authorized Redirect URIs**
  - Only needed if you keep a fallback redirect-based flow.
  ```
  http://localhost:3000/auth/google/callback
  https://yourdomain.com/auth/google/callback
  ```

8. **Copy Credentials**
   - Client ID: `xxxxx.apps.googleusercontent.com`
   - Client Secret: `xxxxxxxxxxxxxxx`

#### Step 3: Update .env File
```bash
# Edit .env or .env.docker
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Frontend .env.local (Next.js)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

#### Step 4: Configure Social App in Django Admin

**Option A: Using Django Admin (Recommended)**
```bash
# 1. Login to admin: http://localhost:8000/admin/
# 2. Go to "Sites" > "Social applications" > "Add social application"
# 3. Fill in:
#    - Provider: Google
#    - Name: Google OAuth
#    - Client id: (paste from Google Console)
#    - Secret key: (paste from Google Console)
#    - Sites: Select "localhost:8000" (or your site)
# 4. Save
```

**Option B: Using Django Shell (Automated)**
```bash
docker compose exec web python manage.py shell

# In Python shell:
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os

# Get credentials from environment
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

# Create or update Google OAuth app
google_app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google OAuth',
        'client_id': client_id,
        'secret': client_secret,
    }
)

if not created:
    google_app.client_id = client_id
    google_app.secret = client_secret
    google_app.save()

# Add current site
site = Site.objects.get_current()
google_app.sites.add(site)

print(f"✅ Google OAuth configured for {site.domain}")
exit()
```

#### Step 5: Update URLs (if needed)

Ensure the authentication routes expose JWT refresh and Google login:

```python
# config/urls.py
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
  path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('api/auth/', include('apps.accounts.urls')),  # /api/auth/google/
  path('api/auth/', include('dj_rest_auth.urls')),
  path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]
```

#### Step 6: Restart Server
```bash
docker compose restart web
```

---

## 🧪 Testing Both Authentication Methods

### Test 1: Email/Password Registration & Login

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password1": "TestPass123!",
    "password2": "TestPass123!"
  }'

# Login with email/password
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "first_name": "",
    "last_name": ""
  }
}
```

### Test 2: Google OAuth Login (After Setup)

**Frontend Flow:**
```javascript
import { useGoogleLogin } from '@react-oauth/google';

const loginWithGoogle = useGoogleLogin({
  onSuccess: async (tokenResponse) => {
    const res = await fetch('http://localhost:8000/api/auth/google/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auth_token: tokenResponse.access_token })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Google login failed');

    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
  },
  onError: () => console.error('Google popup closed or failed'),
});

// Trigger popup
loginWithGoogle();
```

**Direct API Test:**
```bash
# Use a valid Google OAuth access token obtained via Google Identity Services
curl -X POST http://localhost:8000/api/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{
    "auth_token": "ya29.a0AfH6SMB..."
  }'
```

---

## 🔐 Security Configuration

### Development Settings (Current)
```python
# .env
DEBUG=True
ACCOUNT_EMAIL_VERIFICATION='none'
SOCIALACCOUNT_EMAIL_VERIFICATION='none'
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Production Settings (Recommended)
```python
# .env (production)
DEBUG=False
ACCOUNT_EMAIL_VERIFICATION='mandatory'  # Require email verification
SOCIALACCOUNT_EMAIL_VERIFICATION='optional'  # Optional for social
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 📊 User Flow Diagrams

### Email/Password Flow
```
User                    Frontend                Backend
 |                         |                       |
 |-- Enter email/pass ---->|                       |
 |                         |-- POST /auth/login -->|
 |                         |                       |-- Validate credentials
 |                         |                       |-- Generate JWT tokens
 |                         |<-- {access, refresh}--|
 |<-- Store tokens --------|                       |
 |                         |                       |
 |-- API Request --------->|-- + Auth header ----->|
 |                         |                       |-- Verify JWT
 |                         |<-- Protected data ----|
 |<-- Response ------------|                       |
```

### Google OAuth Flow (Token Exchange)
```
User                Frontend                Google                Backend
 |                     |                       |                       |
 |-- Click "Google" ->|                       |                       |
 |                     |-- Popup/login ------->|                       |
 |                     |<-- access_token ------|                       |
 |                     |                       |                       |
 |                     |-- POST /auth/google ----------------------->|
 |                     |    { auth_token }    |                       |
 |                     |                       |-- Validate token -->|
 |                     |                       |<-- Profile data -----|
 |                     |                       |                       |
 |                     |<-- {access, refresh}------------------------|
 |<-- Store tokens ----|                       |                       |
```

---

## 🛠️ Frontend Integration Examples

### React Example

```jsx
import { useGoogleLogin } from '@react-oauth/google';

// Login with Email/Password
const loginWithEmail = async (email, password) => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    
    if (response.ok) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      window.location.href = '/dashboard';
    }
  } catch (error) {
    console.error('Login failed:', error);
  }
};

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const loginWithGoogle = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      const res = await fetch('http://localhost:8000/api/auth/google/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auth_token: tokenResponse.access_token }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Google login failed');
      }
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      window.location.href = '/dashboard';
    },
    onError: () => console.error('Google login cancelled'),
  });
  
  return (
    <div>
      <h1>Login</h1>
      
      {/* Email/Password Form */}
      <form onSubmit={(e) => {
        e.preventDefault();
        loginWithEmail(email, password);
      }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login with Email</button>
      </form>
      
      <hr />
      
      {/* Google OAuth Button */}
      <button onClick={() => loginWithGoogle()}>
        Login with Google
      </button>
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div class="login-page">
    <h1>Login</h1>
    
    <!-- Email/Password Form -->
    <form @submit.prevent="loginWithEmail">
      <input
        v-model="email"
        type="email"
        placeholder="Email"
        required
      />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <button type="submit">Login with Email</button>
    </form>
    
    <hr />
    
    <!-- Google OAuth Button -->
    <button @click="loginWithGoogle">
      Login with Google
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
    };
  },
  methods: {
    async loginWithEmail() {
      try {
        const response = await fetch('http://localhost:8000/api/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);
          this.$router.push('/dashboard');
        }
      } catch (error) {
        console.error('Login failed:', error);
      }
    },
    
    loginWithGoogle() {
      const client = google.accounts.oauth2.initTokenClient({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        scope: 'openid email profile',
        callback: async (tokenResponse) => {
          const response = await fetch('http://localhost:8000/api/auth/google/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ auth_token: tokenResponse.access_token }),
          });

          const data = await response.json();
          if (response.ok) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            this.$router.push('/dashboard');
          } else {
            console.error(data.detail || 'Google login failed');
          }
        },
      });

      client.requestAccessToken();
    },
  },
};
</script>
```

---

## 🔍 Verification Checklist

### ✅ Email/Password Authentication
- [x] Custom user model with email as username
- [x] Registration endpoint working
- [x] Login endpoint working
- [x] JWT token generation
- [x] Token refresh
- [x] Password reset flow
- [x] User profile endpoints
- [x] Protected endpoints with JWT auth

### ⚠️ Google OAuth (Requires Setup)
- [x] Django allauth installed
- [x] Google provider configured
- [x] Settings configured
- [ ] Django Site domain updated
- [ ] Google Cloud project created
- [ ] OAuth credentials obtained
- [ ] Redirect URIs configured
- [ ] SocialApp added to database
- [ ] Frontend integration tested

---

## 📝 Quick Setup Commands

```bash
# 1. Update environment variables
nano .env.docker
# Add:
# GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=your-secret

# 2. Restart containers
docker compose restart

# 3. Update Django site
docker compose exec web python manage.py shell
>>> from django.contrib.sites.models import Site
>>> site = Site.objects.get_current()
>>> site.domain = 'localhost:8000'
>>> site.name = 'ReplyCompass'
>>> site.save()
>>> exit()

# 4. Configure Google OAuth (using admin or shell as shown above)

# 5. Test email/password login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin123!"}'

# 6. Test Google OAuth (requires Google access token)
# curl -X POST http://localhost:8000/api/auth/google/ \
#   -H "Content-Type: application/json" \
#   -d '{"auth_token": "ya29.a0AfH6SMB..."}'
```

---

## 🎯 Summary

### Current Status:
✅ **Email/Password Authentication**: Fully functional  
⚠️ **Google OAuth**: Configured but needs Google Cloud setup

### To Enable Google OAuth:
1. Create Google Cloud project
2. Get OAuth credentials
3. Update `.env` with credentials
4. Configure SocialApp in Django
5. Test the flow

### All Ready for Production:
- JWT-based authentication
- Token refresh mechanism
- CORS configured
- Custom user model
- Both auth methods configured
- Just need Google OAuth credentials!

---

**Last Updated**: December 1, 2025  
**Status**: Email/Password ✅ | Google OAuth ⚠️ (Setup Required)
