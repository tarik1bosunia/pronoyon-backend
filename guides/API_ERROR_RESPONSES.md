# API Error Response Structure

All API errors now return consistent JSON responses with the following structure:

## Standard Error Response Format

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "status_code": 400,
  "details": {
    // Optional: Field-specific errors or additional context
  }
}
```

## Error Types and Examples

### 1. Validation Errors (400)

**Example: Duplicate Email Registration**
```json
{
  "error": "ValidationError",
  "message": "{'email': [ErrorDetail(string='A user with this email already exists.', code='invalid')]}",
  "status_code": 400,
  "details": {
    "email": [
      "A user with this email already exists."
    ]
  }
}
```

**Example: Wrong Login Credentials**
```json
{
  "error": "ValidationError",
  "message": "{'non_field_errors': [ErrorDetail(string='Unable to log in with provided credentials.', code='invalid')]}",
  "status_code": 400,
  "details": {
    "non_field_errors": [
      "Unable to log in with provided credentials."
    ]
  }
}
```

**Example: Missing Required Fields**
```json
{
  "error": "ValidationError",
  "message": "Invalid input",
  "status_code": 400,
  "details": {
    "email": ["This field is required."],
    "password1": ["This field is required."]
  }
}
```

### 2. Authentication Errors (401)

**Example: No Authentication Token**
```json
{
  "error": "NotAuthenticated",
  "message": "Authentication credentials were not provided.",
  "status_code": 401
}
```

**Example: Invalid or Expired Token**
```json
{
  "error": "NotAuthenticated",
  "message": "Token is invalid or expired.",
  "status_code": 401
}
```

### 3. Permission Errors (403)

**Example: Insufficient Permissions**
```json
{
  "error": "PermissionDenied",
  "message": "You do not have permission to perform this action.",
  "status_code": 403
}
```

**Example: RBAC Permission Check Failed**
```json
{
  "error": "PermissionDenied",
  "message": "User lacks required permission: admin.manage_users",
  "status_code": 403
}
```

### 4. Not Found Errors (404)

**Example: Resource Not Found**
```json
{
  "error": "NotFound",
  "message": "The requested resource was not found.",
  "status_code": 404
}
```

**Example: Endpoint Not Found**
```json
{
  "error": "ClientError",
  "message": "The requested resource was not found.",
  "status_code": 404,
  "debug_info": {
    "path": "/api/nonexistent/",
    "method": "GET"
  }
}
```

### 5. Database Integrity Errors (400)

**Example: Duplicate Entry**
```json
{
  "error": "IntegrityError",
  "message": "A user with this email already exists.",
  "status_code": 400,
  "details": {
    "email": ["This email is already registered."]
  }
}
```

**Example: Foreign Key Constraint**
```json
{
  "error": "IntegrityError",
  "message": "Referenced record does not exist.",
  "status_code": 400
}
```

### 6. Server Errors (500)

**Example: Unexpected Server Error**
```json
{
  "error": "ServerError",
  "message": "An unexpected error occurred. Please try again later.",
  "status_code": 500,
  "details": {
    "exception_type": "SomeException",
    "exception_message": "Detailed error message"
  }
}
```

**Note:** In production (DEBUG=False), sensitive error details are hidden from the response.

## Implementation Details

### Custom Exception Handler

Location: `apps/core/exceptions.py`

The custom exception handler (`custom_exception_handler`) catches all exceptions and formats them consistently:

- **Django REST Framework exceptions**: Formatted with error type and details
- **Django ORM IntegrityErrors**: Parsed and converted to user-friendly messages
- **Django's ObjectDoesNotExist**: Converted to 404 responses
- **Django's PermissionDenied**: Converted to 403 responses
- **Unexpected exceptions**: Logged and converted to generic 500 errors

### JSON Error Middleware

Location: `apps/core/middleware.py`

The middleware (`JSONErrorMiddleware`) ensures that:

1. All API endpoints (`/api/*` and `/accounts/*`) return JSON errors
2. HTML error pages are never returned for API requests
3. Non-JSON errors are converted to the standard JSON format
4. Unhandled exceptions are caught and formatted

### Configuration

In `config/settings/base.py`:

```python
REST_FRAMEWORK = {
    ...
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    ...
}

MIDDLEWARE = [
    ...
    'apps.core.middleware.JSONErrorMiddleware',  # Should be last
]
```

## Benefits

1. **Consistency**: All errors follow the same structure
2. **Client-Friendly**: Easy to parse and display in frontend applications
3. **Debugging**: Debug info included in development mode
4. **Security**: Sensitive details hidden in production
5. **Logging**: All errors are logged for monitoring
6. **API-First**: No HTML responses for API endpoints

## Testing Error Responses

### Using cURL

```bash
# Test duplicate email
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{"email":"existing@example.com","password1":"pass123","password2":"pass123"}'

# Test authentication error
curl -X GET http://localhost:8000/api/auth/user/

# Test 404 error
curl -X GET http://localhost:8000/api/nonexistent/

# Test wrong credentials
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@replycompass.com","password":"wrongpassword"}'
```

### Using Postman

Import the collection from `postman/ReplyCompass_API.postman_collection.json` and test error scenarios:

1. Try registering with an existing email
2. Try accessing protected endpoints without a token
3. Try logging in with wrong credentials
4. Try accessing non-existent resources

### Using Jupyter Notebooks

Run the notebooks in `notebooks/` directory to see comprehensive error handling examples.

## Error Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error` | string | Yes | Error type/class name (e.g., "ValidationError", "NotAuthenticated") |
| `message` | string | Yes | Human-readable error message for display to users |
| `status_code` | integer | Yes | HTTP status code (400, 401, 403, 404, 500, etc.) |
| `details` | object | No | Field-specific errors or additional context (validation errors, debug info) |

## Status Code Reference

| Code | Error Type | Common Causes |
|------|------------|---------------|
| 400 | ValidationError / IntegrityError | Invalid input, duplicate entries, missing fields |
| 401 | NotAuthenticated | Missing token, expired token, invalid token |
| 403 | PermissionDenied | Insufficient permissions, RBAC check failed |
| 404 | NotFound | Resource doesn't exist, endpoint not found |
| 405 | MethodNotAllowed | Wrong HTTP method (e.g., GET instead of POST) |
| 429 | Throttled | Too many requests, rate limit exceeded |
| 500 | ServerError | Unexpected server error, unhandled exception |

## Best Practices

### For Frontend Developers

1. **Always check `status_code`** to determine error type
2. **Display `message`** to users for general errors
3. **Parse `details`** for field-specific validation errors
4. **Handle common status codes**:
   - 400: Show validation errors next to form fields
   - 401: Redirect to login page
   - 403: Show "Permission denied" message
   - 404: Show "Not found" page
   - 500: Show "Server error, try again later"

### Example Error Handling (JavaScript)

```javascript
try {
  const response = await fetch('/api/auth/registration/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    // Handle error based on status code
    switch (data.status_code) {
      case 400:
        // Show field-specific errors
        if (data.details) {
          Object.keys(data.details).forEach(field => {
            showFieldError(field, data.details[field][0]);
          });
        } else {
          showGeneralError(data.message);
        }
        break;
      
      case 401:
        // Redirect to login
        window.location.href = '/login';
        break;
      
      case 403:
        showGeneralError('You do not have permission to perform this action');
        break;
      
      case 404:
        showGeneralError('The requested resource was not found');
        break;
      
      case 500:
        showGeneralError('An unexpected error occurred. Please try again later');
        break;
      
      default:
        showGeneralError(data.message);
    }
  }
} catch (error) {
  console.error('Network error:', error);
  showGeneralError('Unable to connect to the server');
}
```

## Debugging

### Development Mode (DEBUG=True)

- Includes `debug_info` in error responses
- Shows exception types and messages
- Includes request path and method

### Production Mode (DEBUG=False)

- Hides sensitive error details
- Shows user-friendly messages only
- Logs all errors server-side

### Viewing Logs

```bash
# View all logs
docker compose logs -f web

# View only error logs
docker compose logs -f web | grep ERROR

# View logs in real-time
make dev-logs
```

## Migration from Old Error Format

### Before (HTML Responses)

```html
<!DOCTYPE html>
<html>
<head><title>Server Error (500)</title></head>
<body>
  <h1>Server Error (500)</h1>
  <p>IntegrityError: duplicate key value violates unique constraint "users_email_key"</p>
</body>
</html>
```

### After (JSON Responses)

```json
{
  "error": "IntegrityError",
  "message": "A user with this email already exists.",
  "status_code": 400,
  "details": {
    "email": ["This email is already registered."]
  }
}
```

## Related Files

- **Exception Handler**: `apps/core/exceptions.py`
- **Middleware**: `apps/core/middleware.py`
- **Settings**: `config/settings/base.py`
- **Custom Serializer**: `apps/accounts/serializers.py`
- **Tests**: Can be added to test error responses

---

**Last Updated**: November 14, 2025  
**Version**: 1.0.0
