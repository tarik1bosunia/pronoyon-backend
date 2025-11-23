# API Testing Notebooks

Interactive Jupyter notebooks for testing all ReplyCompass API endpoints.

## 📚 Notebooks Overview

### 00_complete_overview.ipynb
**Complete system overview and testing**
- Discover all available endpoints
- Test authentication flow
- Test RBAC system
- Filter and search capabilities
- Error handling
- Pagination testing

### 01_authentication_endpoints.ipynb
**Authentication & User Management**
- User registration (email-based, no username)
- Login/Logout
- JWT token management (access & refresh)
- Password change
- Password reset flow
- Current user profile
- Error scenarios testing

### 02_rbac_endpoints.ipynb
**Role-Based Access Control (RBAC)**
- List/Create/Update/Delete roles
- Manage permissions
- User role assignments
- Current user RBAC info
- Role filtering by level
- Permission search
- Comprehensive role analysis

### 03_google_oauth.ipynb
**Google OAuth Authentication**
- Google OAuth flow
- Configuration check
- Token-based login
- Frontend integration examples

## 🚀 Getting Started

### 1. Install Jupyter

```bash
# Using pip
pip install jupyter notebook requests

# Or using conda
conda install jupyter notebook requests
```

### 2. Start Jupyter Notebook

```bash
cd /home/tata/tarik/replycompass
jupyter notebook
```

This will open Jupyter in your browser at `http://localhost:8888`

### 3. Navigate to Notebooks

In Jupyter, navigate to the `notebooks/` directory and open any notebook.

### 4. Run the Cells

- Click on a cell and press `Shift + Enter` to run it
- Or use the "Run" button in the toolbar
- Run cells in order from top to bottom

## 📋 Prerequisites

### 1. Make sure the development server is running:

```bash
make dev
# or
docker compose up
```

### 2. Verify the API is accessible:

```bash
curl http://localhost:8000/api/auth/login/
```

## 🔐 Authentication

Most endpoints require authentication. The notebooks handle this automatically:

1. Run the login cell first
2. The notebook stores the JWT token
3. Subsequent requests use the stored token

Default credentials:
- **Email**: `admin@replycompass.com`
- **Password**: `admin123`

## 📊 What You Can Test

### Authentication
- ✅ Email-based registration (no username field)
- ✅ Login with email & password
- ✅ JWT token generation
- ✅ Token refresh
- ✅ Password change/reset
- ✅ User profile retrieval

### RBAC System
- ✅ 9 predefined roles (Guest to Super Admin)
- ✅ 32+ permissions across 7 resources
- ✅ User role assignments
- ✅ Permission checking
- ✅ Role hierarchy (levels 0-100)

### Filters & Search
- ✅ Role filtering by level
- ✅ Permission search by name/resource
- ✅ User role filtering
- ✅ Pagination support

## 🎯 Common Use Cases

### Test New User Registration
Open `01_authentication_endpoints.ipynb` and run the registration cell with your test data.

### Check User's Permissions
Open `02_rbac_endpoints.ipynb` and run the "Get Current User's RBAC Info" cell.

### Create Custom Role
Open `02_rbac_endpoints.ipynb` and use the "Create New Role" cell.

### Test OAuth Flow
Open `03_google_oauth.ipynb` to test Google authentication.

## 🔍 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/schema/swagger/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 💡 Tips

1. **Run cells in order**: Notebooks are designed to be run sequentially
2. **Login first**: Authentication cells should be run before testing protected endpoints
3. **Check status codes**: Each response shows the HTTP status code
4. **Read error messages**: Failed requests display detailed error information
5. **Modify test data**: Feel free to change the test data in cells to experiment

## 🛠️ Troubleshooting

### "Connection refused" error
- Make sure Docker containers are running: `docker compose ps`
- Check if web service is healthy: `curl http://localhost:8000`

### "Authentication credentials were not provided"
- Run the login cell first to get an access token
- Check if the token is stored correctly

### "Invalid token" error
- Token might have expired (default: 1 hour)
- Re-run the login cell to get a fresh token

## 📝 Example Workflow

1. Start Docker containers
   ```bash
   make dev
   ```

2. Start Jupyter
   ```bash
   jupyter notebook
   ```

3. Open `00_complete_overview.ipynb`

4. Run all cells to get a complete system overview

5. Open specific notebooks for detailed testing:
   - Authentication → `01_authentication_endpoints.ipynb`
   - RBAC → `02_rbac_endpoints.ipynb`
   - OAuth → `03_google_oauth.ipynb`

## 🎓 Learning Path

**Beginner**: Start with `00_complete_overview.ipynb` to understand the system

**Intermediate**: Use `01_authentication_endpoints.ipynb` and `02_rbac_endpoints.ipynb` for detailed testing

**Advanced**: Modify notebooks to create custom test scenarios and automate testing

## 📚 Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication Guide](https://jwt.io/introduction)
- [RBAC Best Practices](https://en.wikipedia.org/wiki/Role-based_access_control)
- [API Testing Best Practices](https://www.postman.com/api-testing/)

## 🤝 Contributing

Feel free to add new notebooks for testing additional features or improving existing ones!

## 📄 License

Same as the main project.
