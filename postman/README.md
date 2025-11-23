# 🚀 ReplyCompass API - Postman Collection

Complete Postman collection for testing all ReplyCompass API endpoints.

## 📦 Files in this Directory

1. **ReplyCompass_API.postman_collection.json** - Main collection with all endpoints
2. **ReplyCompass.postman_environment.json** - Environment variables (local development)
3. **openapi_schema.json** - OpenAPI 3.0 specification (alternative import method)

## 🎯 Quick Start

### Method 1: Import Pre-configured Collection (RECOMMENDED)

1. **Open Postman** (download from https://www.postman.com/downloads/ if needed)

2. **Import Collection**
   - Click "Import" button in Postman
   - Select `ReplyCompass_API.postman_collection.json`
   - Click "Import"

3. **Import Environment**
   - Click "Import" button again
   - Select `ReplyCompass.postman_environment.json`
   - Click "Import"

4. **Select Environment**
   - Click the environment dropdown (top-right)
   - Select "ReplyCompass - Local"

5. **Start Testing!** 🎉

### Method 2: Import from OpenAPI Schema

1. **Open Postman**
2. Click "Import" → "Link"
3. Enter: `http://localhost:8000/api/schema/`
4. Or upload `openapi_schema.json` file
5. Postman will auto-generate the collection

## 🔑 Authentication Flow

### First Time Setup

1. **Login to Get Tokens**
   - Open "Authentication" folder
   - Click "Login" request
   - Body already has: `{"email": "admin@replycompass.com", "password": "admin123"}`
   - Click "Send"
   - Tokens are **automatically saved** to environment variables!

2. **Verify Token Storage**
   - Click environment dropdown → "ReplyCompass - Local"
   - Check `access_token` and `refresh_token` are now filled

3. **All Authenticated Requests Now Work!**
   - The collection is configured to use `{{access_token}}` automatically
   - No need to manually copy/paste tokens

### Token Management

- **Access Token Expires?** → Use "Refresh Token" request
- **Need to Re-login?** → Use "Login" request again
- **Test Without Auth?** → Uncheck "Authorization" tab in specific request

## 📂 Collection Structure

### 🔐 Authentication (8 endpoints)
- ✅ Register User - Create new account
- ✅ Login - Get JWT tokens (auto-saves tokens)
- ✅ Get Current User - View profile
- ✅ Refresh Token - Get new access token (auto-updates)
- ✅ Logout - Invalidate tokens
- ✅ Change Password - Update password
- ✅ Password Reset Request - Request reset email
- ✅ Password Reset Confirm - Complete reset

### 👤 RBAC - Roles (6 endpoints)
- ✅ List Roles - Get all roles
- ✅ Get Role Details - View specific role
- ✅ Create Role - Add new role
- ✅ Update Role - Modify existing role
- ✅ Delete Role - Remove role
- ✅ Filter Roles by Level - Find roles >= certain level

### 🔒 RBAC - Permissions (5 endpoints)
- ✅ List Permissions - Get all permissions
- ✅ Get Permission Details - View specific permission
- ✅ Create Permission - Add new permission
- ✅ Search Permissions - Find by name/resource
- ✅ Filter by Resource - Get permissions for specific resource

### 👥 RBAC - User Roles (4 endpoints)
- ✅ List User Role Assignments - See all user-role mappings
- ✅ Assign Role to User - Grant role to user
- ✅ Get Current User RBAC Info - View your roles & permissions
- ✅ Remove User Role - Revoke role from user

### 🌐 Google OAuth (2 endpoints)
- ✅ Initiate Google Login - Start OAuth flow
- ✅ Login with Google Token - Complete frontend OAuth

**Total: 25 endpoints** covering all API functionality!

## 🎓 Usage Examples

### Example 1: Complete Registration Flow

1. **Register New User**
   ```
   POST /api/auth/registration/
   Body: {
     "email": "newuser@example.com",
     "password1": "SecurePass123!",
     "password2": "SecurePass123!"
   }
   ```
   ✅ Returns JWT tokens (auto-saved)

2. **Get User Profile**
   ```
   GET /api/auth/user/
   Authorization: Bearer {{access_token}}
   ```
   ✅ Returns user details with RBAC info

### Example 2: RBAC Management

1. **Login as Admin**
   ```
   POST /api/auth/login/
   Body: {"email": "admin@replycompass.com", "password": "admin123"}
   ```

2. **Create Custom Role**
   ```
   POST /api/rbac/roles/
   Body: {
     "name": "Content Manager",
     "description": "Manages content",
     "level": 50
   }
   ```

3. **Assign Role to User**
   ```
   POST /api/rbac/user-roles/
   Body: {"user": 2, "role": 3}
   ```

4. **Verify Assignment**
   ```
   GET /api/rbac/current-user/
   ```
   ✅ Shows roles & permissions for current user

### Example 3: Permission Filtering

1. **Find All Admin Permissions**
   ```
   GET /api/rbac/permissions/?resource=admin
   ```

2. **Search by Name**
   ```
   GET /api/rbac/permissions/?search=user
   ```

3. **Get Roles with High Level**
   ```
   GET /api/rbac/roles/?level__gte=80
   ```

## 🔧 Environment Variables

| Variable | Description | Auto-Updated |
|----------|-------------|--------------|
| `base_url` | API base URL | ❌ Manual |
| `access_token` | JWT access token | ✅ Auto (login/refresh) |
| `refresh_token` | JWT refresh token | ✅ Auto (login) |
| `user_email` | Test user email | ❌ Manual |
| `user_password` | Test user password | ❌ Manual |

### Switching Environments

**Local Development:**
```json
"base_url": "http://localhost:8000"
```

**Production:**
```json
"base_url": "https://api.replycompass.com"
```

Just change the `base_url` variable in your environment!

## 🧪 Testing Features

### Auto-Save Tokens (Built-in!)

The collection includes **test scripts** that automatically save tokens:

```javascript
// Login and Register requests auto-save tokens
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.collectionVariables.set('access_token', jsonData.access);
    pm.collectionVariables.set('refresh_token', jsonData.refresh);
}
```

### Manual Token Update

If needed, you can manually update tokens:
1. Click environment dropdown → "ReplyCompass - Local"
2. Edit `access_token` or `refresh_token` values
3. Click "Save"

## 🌐 Alternative Testing Methods

### 1. Swagger UI (Browser-based)
```bash
# Open in browser
http://localhost:8000/api/schema/swagger/
```
✅ Interactive, no installation needed
✅ Built-in authentication
❌ No environment variables

### 2. ReDoc (Documentation)
```bash
# Open in browser
http://localhost:8000/api/schema/redoc/
```
✅ Beautiful documentation
✅ Examples included
❌ Read-only (no testing)

### 3. Jupyter Notebooks (Interactive Python)
```bash
cd notebooks/
jupyter notebook
```
✅ Great for learning
✅ Can modify and experiment
❌ Requires Python setup

### 4. cURL (Command Line)
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@replycompass.com","password":"admin123"}'

# Use token
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
✅ Quick testing
✅ Scriptable
❌ Manual token management

## 🚨 Common Issues & Solutions

### Issue: "Unauthenticated" Error

**Solution:**
1. Click "Login" request
2. Verify credentials in body
3. Click "Send"
4. Token should auto-save to environment
5. If not, manually copy token to `access_token` variable

### Issue: "Token Expired" Error

**Solution:**
1. Use "Refresh Token" request
2. Or re-login with "Login" request
3. Token will be automatically updated

### Issue: Can't See Environment Variables

**Solution:**
1. Check environment is selected (top-right dropdown)
2. Import environment file if missing
3. Click environment name to view/edit variables

### Issue: Base URL Wrong

**Solution:**
1. Ensure Django server is running: `make dev`
2. Check `base_url` in environment: `http://localhost:8000`
3. No trailing slash in base URL

### Issue: "CSRF Token Missing" Error

**Solution:**
- This API uses JWT (not sessions), CSRF not needed
- Ensure "Authorization: Bearer {{access_token}}" header is present
- Check token is valid (not expired)

## 📊 Response Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed |
| 201 | Created | Resource created successfully |
| 204 | No Content | Deletion successful |
| 400 | Bad Request | Check request body/params |
| 401 | Unauthorized | Login or refresh token |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify endpoint/resource ID |
| 500 | Server Error | Check Django logs |

## 🎨 Customization

### Add New Request

1. Right-click folder → "Add Request"
2. Set method (GET, POST, etc.)
3. Enter URL: `{{base_url}}/your/endpoint/`
4. Add body (JSON) if needed
5. Authorization is inherited from collection

### Create Test Script

Add to request's "Tests" tab:
```javascript
pm.test("Status is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('data');
});
```

### Variables in Request Body

Use `{{variable_name}}` syntax:
```json
{
  "email": "{{user_email}}",
  "password": "{{user_password}}"
}
```

## 📚 Additional Resources

- **Django Project**: `/home/tata/tarik/replycompass/`
- **Jupyter Notebooks**: `notebooks/` directory
- **OpenAPI Schema**: `postman/openapi_schema.json`
- **Django Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/schema/swagger/

## 🤝 Support

### Need Help?

1. **Check Django Server**
   ```bash
   make dev  # Ensure server is running
   ```

2. **View Logs**
   ```bash
   docker compose logs -f backend
   ```

3. **Test Endpoints in Notebook**
   ```bash
   cd notebooks/
   jupyter notebook 00_complete_overview.ipynb
   ```

### Testing Checklist

- [ ] Django server running (`make dev`)
- [ ] Postman collection imported
- [ ] Environment selected
- [ ] Logged in (tokens saved)
- [ ] Base URL correct (`http://localhost:8000`)

## 🎯 Quick Reference

### Default Admin Credentials
```
Email: admin@replycompass.com
Password: admin123
```

### Key Endpoints
```
Auth:  http://localhost:8000/api/auth/
RBAC:  http://localhost:8000/api/rbac/
Docs:  http://localhost:8000/api/schema/swagger/
Admin: http://localhost:8000/admin/
```

### Important Headers
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

---

**Ready to Test?** 🚀

1. Import collection & environment
2. Select "ReplyCompass - Local" environment
3. Click "Login" request → Send
4. Start testing all endpoints!

**Happy Testing!** 🎉
