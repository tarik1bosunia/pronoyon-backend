# Django CORS Headers Configuration Guide

## Overview

This guide explains how to install and configure `django-cors-headers` for your ReplyCompass Django project. CORS (Cross-Origin Resource Sharing) is essential for allowing your frontend application to communicate with your Django backend API.

---

## Table of Contents

1. [What is CORS?](#what-is-cors)
2. [Why Do We Need It?](#why-do-we-need-it)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Environment-Based Setup](#environment-based-setup)
6. [Testing CORS](#testing-cors)
7. [Common Issues & Solutions](#common-issues--solutions)
8. [Security Best Practices](#security-best-practices)

---

## What is CORS?

**CORS (Cross-Origin Resource Sharing)** is a security feature implemented by web browsers that restricts web pages from making requests to a different domain than the one that served the web page.

### Example Scenario:

```
Frontend:  http://localhost:3000        (React/Vue/Angular)
Backend:   http://localhost:8000        (Django API)
          ↑
          Different origins - CORS needed!
```

Without CORS configuration, the browser will block requests from your frontend to your backend API.

---

## Why Do We Need It?

### **ReplyCompass Use Cases:**

1. **Frontend-Backend Separation**
   - React/Vue/Angular frontend on `http://localhost:3000`
   - Django API backend on `http://localhost:8000`

2. **Mobile Apps**
   - Mobile applications making API requests

3. **Third-Party Integrations**
   - External services accessing your API

4. **Multiple Domains**
   - Production: `https://app.replycompass.com` → `https://api.replycompass.com`

---

## Installation

### Step 1: Install Package

The package is already included in your `requirements.txt`:

```bash
# Activate virtual environment
source venv/bin/activate

# Install from requirements.txt
pip install django-cors-headers

# Or install separately
pip install django-cors-headers==4.3.1
```

### Step 2: Verify Installation

```bash
pip show django-cors-headers
```

**Expected Output:**
```
Name: django-cors-headers
Version: 4.3.1
Summary: django-cors-headers is a Django application for handling the server headers required for Cross-Origin Resource Sharing (CORS).
```

---

## Configuration

### Step 1: Add to INSTALLED_APPS

Already configured in `config/settings/base.py`:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',  # ✅ Add this BEFORE django.contrib apps
    'django.contrib.admin',
    # ...
]
```

**⚠️ Important:** Place `corsheaders` **before** `django.contrib.apps` to ensure proper middleware ordering.

---

### Step 2: Add Middleware

Already configured in `config/settings/base.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ✅ Add this
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

**⚠️ Important:** 
- Place `CorsMiddleware` **before** `CommonMiddleware`
- Place it **after** `SessionMiddleware`

---

### Step 3: Configure CORS Settings

Already configured in `config/settings/base.py`:

```python
# =============================================================================
# CORS SETTINGS
# =============================================================================

# Allowed origins from environment variable
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

# Allow credentials (cookies, authentication headers)
CORS_ALLOW_CREDENTIALS = True

# Allowed HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allowed headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Frontend URL
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
```

---

## Environment-Based Setup

### Development (.env file)

```env
# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173
FRONTEND_URL=http://localhost:3000
```

### Docker Development (.env file)

```env
# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Production (.env file)

```env
# CORS Configuration
CORS_ALLOWED_ORIGINS=https://app.replycompass.com,https://www.replycompass.com
FRONTEND_URL=https://app.replycompass.com
```

---

## CORS Configuration Options

### Option 1: Specific Origins (Recommended)

```python
# Best for production - explicit whitelist
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://app.replycompass.com',
]
```

**Pros:**
- ✅ Most secure
- ✅ Explicit control
- ✅ Recommended for production

---

### Option 2: Allow All Origins (Development Only)

```python
# Only use in local development!
CORS_ALLOW_ALL_ORIGINS = True
```

**Pros:**
- ✅ Quick setup for development
- ✅ No configuration needed

**Cons:**
- ❌ **NEVER use in production!**
- ❌ Security risk
- ❌ Allows any website to access your API

---

### Option 3: Origin Regex (Advanced)

```python
# Allow all subdomains
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.replycompass\.com$",
]
```

**Use case:** Multiple subdomains (staging, preview, etc.)

---

## Complete Configuration Example

### For Local Development

**File: `config/settings/local.py`**

```python
from .base import *

# Allow all origins in local development
CORS_ALLOW_ALL_ORIGINS = True

# Or specify origins
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',
#     'http://localhost:5173',  # Vite default
#     'http://127.0.0.1:3000',
# ]

CORS_ALLOW_CREDENTIALS = True
```

---

### For Docker Development

**File: `config/settings/docker.py`**

```python
from .base import *

# Load from environment
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
```

---

### For Production

**File: `config/settings/production.py`**

```python
from .base import *

# Strict origin whitelist from environment
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# Must be explicit in production - NO ALLOW_ALL!
CORS_ALLOW_CREDENTIALS = True
FRONTEND_URL = config('FRONTEND_URL')

# Additional production security
CORS_ALLOW_PRIVATE_NETWORK = False
```

---

## Testing CORS

### Method 1: Using cURL

```bash
# Test preflight OPTIONS request
curl -X OPTIONS http://localhost:8000/api/users/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -i

# Expected headers in response:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Credentials: true
```

---

### Method 2: Using Browser Console

Open your frontend application and run:

```javascript
// Test API request
fetch('http://localhost:8000/api/users/', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  }
})
.then(response => response.json())
.then(data => console.log('✅ CORS working!', data))
.catch(error => console.error('❌ CORS error:', error));
```

---

### Method 3: Check Browser Network Tab

1. Open DevTools (F12)
2. Go to **Network** tab
3. Make an API request
4. Click on the request
5. Check **Response Headers**:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

---

## Common Issues & Solutions

### Issue 1: CORS Error Despite Configuration

**Error:**
```
Access to fetch at 'http://localhost:8000/api/' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

**Solutions:**

1. **Check Middleware Order**
   ```python
   # WRONG
   MIDDLEWARE = [
       'django.middleware.common.CommonMiddleware',
       'corsheaders.middleware.CorsMiddleware',  # ❌ Too late
   ]
   
   # CORRECT
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',  # ✅ Before CommonMiddleware
       'django.middleware.common.CommonMiddleware',
   ]
   ```

2. **Verify Origin Format**
   ```python
   # WRONG
   CORS_ALLOWED_ORIGINS = [
       'localhost:3000',  # ❌ Missing protocol
       'http://localhost:3000/',  # ❌ Trailing slash
   ]
   
   # CORRECT
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:3000',  # ✅ Correct format
   ]
   ```

3. **Check .env File**
   ```bash
   # Verify value
   cat .env | grep CORS_ALLOWED_ORIGINS
   
   # Should show:
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

---

### Issue 2: Credentials Not Working

**Error:**
```
Credentials flag is 'true', but the 'Access-Control-Allow-Credentials' 
header is not set
```

**Solution:**
```python
# Enable credentials
CORS_ALLOW_CREDENTIALS = True

# Make sure origin is explicit (not '*')
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # ✅ Explicit origin
]

# NOT this:
# CORS_ALLOW_ALL_ORIGINS = True  # ❌ Can't use with credentials
```

---

### Issue 3: Preflight Requests Failing

**Error:**
```
Response to preflight request doesn't pass access control check
```

**Solution:**

1. **Add OPTIONS to CSRF exempt (if needed)**
   ```python
   # config/urls.py
   from django.views.decorators.csrf import csrf_exempt
   ```

2. **Check allowed methods**
   ```python
   CORS_ALLOW_METHODS = [
       'DELETE',
       'GET',
       'OPTIONS',  # ✅ Make sure OPTIONS is included
       'PATCH',
       'POST',
       'PUT',
   ]
   ```

---

### Issue 4: Custom Headers Not Allowed

**Error:**
```
Request header field 'x-custom-header' is not allowed
```

**Solution:**
```python
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-custom-header',  # ✅ Add your custom header
    'x-csrftoken',
]
```

---

## Security Best Practices

### ✅ DO's

1. **Use Explicit Origins in Production**
   ```python
   # Production
   CORS_ALLOWED_ORIGINS = [
       'https://app.replycompass.com',
       'https://www.replycompass.com',
   ]
   ```

2. **Enable Credentials Only When Needed**
   ```python
   # Only if you need cookies/auth headers
   CORS_ALLOW_CREDENTIALS = True
   ```

3. **Use Environment Variables**
   ```python
   # Load from .env
   CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
   ```

4. **Restrict Methods**
   ```python
   # Only allow what you need
   CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
   ```

---

### ❌ DON'Ts

1. **Never Use `CORS_ALLOW_ALL_ORIGINS = True` in Production**
   ```python
   # ❌ NEVER in production!
   CORS_ALLOW_ALL_ORIGINS = True
   ```

2. **Don't Use Wildcard with Credentials**
   ```python
   # ❌ This combination is forbidden
   CORS_ALLOWED_ORIGINS = ['*']
   CORS_ALLOW_CREDENTIALS = True
   ```

3. **Don't Expose Sensitive Headers**
   ```python
   # ❌ Don't expose these
   CORS_EXPOSE_HEADERS = [
       'Set-Cookie',  # Security risk
       'Authorization',  # Security risk
   ]
   ```

4. **Don't Allow Dangerous Methods Unnecessarily**
   ```python
   # ❌ Only if you really need them
   CORS_ALLOW_METHODS = ['TRACE', 'CONNECT']
   ```

---

## Advanced Configuration

### Preflight Max Age (Caching)

```python
# Cache preflight requests for 1 hour
CORS_PREFLIGHT_MAX_AGE = 3600
```

### Expose Custom Headers

```python
# Allow frontend to access custom response headers
CORS_EXPOSE_HEADERS = [
    'X-Total-Count',
    'X-Page-Number',
]
```

### Different Settings Per URL

```python
# urls.py
from corsheaders.decorators import cors_headers

@cors_headers(allow_origins=['https://trusted-site.com'])
def special_view(request):
    return JsonResponse({'data': 'value'})
```

---

## Verification Checklist

Before deploying, verify:

- [ ] `corsheaders` installed (`pip show django-cors-headers`)
- [ ] Added to `INSTALLED_APPS` (before `django.contrib`)
- [ ] `CorsMiddleware` in `MIDDLEWARE` (before `CommonMiddleware`)
- [ ] `CORS_ALLOWED_ORIGINS` configured in `.env`
- [ ] `CORS_ALLOW_CREDENTIALS` set appropriately
- [ ] Tested with frontend application
- [ ] Checked browser DevTools Network tab
- [ ] No `CORS_ALLOW_ALL_ORIGINS = True` in production
- [ ] HTTPS origins in production `.env`

---

## Quick Reference

### Minimal Configuration

```python
# settings.py
INSTALLED_APPS = [
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
CORS_ALLOW_CREDENTIALS = True
```

### Environment Variables

```env
# .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
FRONTEND_URL=http://localhost:3000
```

---

## Testing Commands

```bash
# Test with curl
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/api/users/ -i

# Check settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
>>> print(settings.CORS_ALLOW_CREDENTIALS)
```

---

## Resources

- **Official Documentation:** https://github.com/adamchainz/django-cors-headers
- **CORS Explained:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- **Django Settings:** https://docs.djangoproject.com/en/4.2/ref/settings/

---

## Summary

✅ **django-cors-headers** is essential for ReplyCompass to allow:
- Frontend (React/Vue/Angular) to communicate with Django API
- Different domains to access your API
- Secure cross-origin requests with proper authentication

✅ **Already configured** in your `base.py` settings!

✅ **Just update** your `.env` file with appropriate origins for your environment.

✅ **Test thoroughly** before deploying to production!

---

**Ready to test CORS with your frontend application!** 🚀
