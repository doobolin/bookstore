# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a bilingual (Chinese) online bookstore management system consisting of:
- **Backend**: Python Flask REST API
- **Admin Frontend**: Vue 3 + TypeScript management interface (administrators only)
- **Public Frontend**: Vue 3 + TypeScript customer-facing bookstore
- **Database**: MySQL with comprehensive schema for users, books, categories, permissions, and sales

## Project Structure

```
D:\AAA\
├── backend/                    # Flask REST API server
│   ├── app.py                  # Main Flask application with all API endpoints
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Database credentials (not in version control)
│   └── venv/                   # Python virtual environment
├── 图书后台管理/               # Admin management system (Vue 3 + TS)
│   ├── src/
│   │   ├── api/                # API client modules (axios)
│   │   ├── views/              # Main views (Login, Home, BookManage, UserManage)
│   │   └── router/             # Vue Router with auth guards
│   └── vite.config.ts          # Vite config with proxy to :5000
├── 线上图书系统/               # Public bookstore (Vue 3 + TS)
│   ├── src/
│   │   ├── components/         # Book components (Home, Login, Register, BookDetail, ShoppingCart)
│   │   ├── api/                # API modules (currently empty)
│   │   ├── store/              # State management (currently empty)
│   │   └── router/             # Vue Router
│   └── vite.config.ts          # Vite config with path aliases
└── mysql_database.sql          # Complete database schema with sample data
```

## Development Commands

### Backend (Flask API)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
# Server starts on http://localhost:5000
```

### Admin Frontend (图书后台管理)

```bash
# Navigate to admin directory
cd 图书后台管理

# Install dependencies
npm install

# Run development server
npm run dev
# Server starts on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

### Public Frontend (线上图书系统)

```bash
# Navigate to public system directory
cd 线上图书系统

# Install dependencies
npm install

# Run development server
npm run dev
# Opens browser automatically

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database Setup

```bash
# Import database schema (from root directory)
mysql -u root -p < mysql_database.sql

# Or connect to MySQL and run:
source D:\AAA\mysql_database.sql
```

## Architecture & Key Concepts

### Backend Architecture

**Flask application uses raw SQL queries instead of ORM models:**
- All database operations use `db.session.execute(text('SQL query'))` with SQLAlchemy
- API responses follow a consistent format: `{ code: number, message: string, data?: any }`
- Helper function `make_response(data, message, status)` standardizes all responses
- CORS is not explicitly configured (needs to be added if frontends are on different origins)

**Special behaviors to be aware of:**
- User deletion reindexes all user IDs sequentially (1, 2, 3, ...) to maintain continuity
- Book addition fills the smallest available ID gap when books are deleted
- No JWT authentication - uses simple mock tokens like `'mock-jwt-token-{username}-{user_id}'`
- Passwords are stored in plain text (⚠️ not secure, needs bcrypt hashing)

**Environment configuration:**
- Database credentials in `backend/.env` (not tracked in git)
- Default database: `bookstore_management_system`

### Frontend Architecture

**Admin System (图书后台管理):**
- **Role-based access control**: Only users with `role === 'admin'` can access
- **Route guards**: `router.beforeEach()` checks `localStorage.getItem('isLoggedIn')` and `localStorage.getItem('role')`
- **API proxy**: Vite proxies `/api/*` requests to `http://localhost:5000`
- **Main views**:
  - `LoginView.vue` - Admin login
  - `HomeView.vue` - Dashboard with nested routes
  - `BookManageView.vue` - CRUD operations for books
  - `UserManageView.vue` - CRUD operations for users
- **API layer**: Centralized axios instance in `api/axiosInstance.ts` with request/response interceptors

**Public System (线上图书系统):**
- **Customer-facing interface**: Browse books, view details, shopping cart
- **Components**:
  - `Home.vue` - Main book browsing interface
  - `Login.vue` / `Register.vue` - User authentication
  - `BookDetail.vue` - Individual book view
  - `ShoppingCart.vue` - Shopping cart functionality
- **Note**: API and store directories are currently empty (implementations may be in components)

### Database Schema

**Core tables:**
- `users` - System users with roles (admin/user) and status (active/inactive)
- `books` - Book catalog with category, price, stock, rating
- `categories` - Book categories (技术, 文学, 历史, etc.)
- `permissions` - Fine-grained permission system
- `role_permissions` - Role-permission mapping
- `operation_logs` - Audit trail of system operations
- `sales_records` - Transaction history
- `reviews` - User book reviews and ratings

**Views:**
- `v_active_users` - Only active users
- `v_book_with_category` - Books with category names joined
- `v_popular_books` - Top 10 books by rating (≥4.5)

**Important indexes:**
- Users: `idx_username`, `idx_email`
- Books: `idx_title`, `idx_author`, `idx_category_id`
- Operation logs: `idx_user_id`, `idx_created_at`

### Authentication Flow

1. User submits credentials to `/api/login`
2. Backend validates against `users` table (plain password comparison)
3. Backend returns mock token, username, and role
4. Frontend stores in localStorage: `token`, `username`, `role`, `isLoggedIn`
5. Admin frontend checks role on route navigation
6. API requests include `Authorization: Bearer {token}` header (though not validated by backend)

### API Endpoints

**User management:**
- `GET /api/users` - Get all users
- `GET /api/users/count` - Get user statistics
- `POST /api/users` - Add user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user (reindexes IDs!)
- `PATCH /api/users/:id/status` - Toggle active/inactive status
- `POST /api/login` - User login
- `POST /api/check-user-status` - Check if user is banned

**Book management:**
- `GET /api/books` - Get all books with categories (uses JOIN, not view)
- `GET /api/books/count` - Get book statistics
- `GET /api/books/low-stock` - Get books with stock < 20
- `POST /api/books` - Add book (fills ID gaps)
- `PUT /api/books/:id` - Update book
- `DELETE /api/books/:id` - Delete book (does NOT reindex IDs)

**System:**
- `GET /api/health` - Health check
- `GET /api/info` - Application info
- `GET /api/test-connection` - Test database connection
- `GET /api/db-version` - Get MySQL version
- `GET /api/check-users-table` - Inspect users table schema

## Common Development Patterns

### Adding a new API endpoint

1. Add route in `backend/app.py`:
```python
@app.route('/api/endpoint', methods=['POST'])
def endpoint_name():
    try:
        from flask import request
        data = request.get_json()

        with app.app_context():
            # Database operations using text() queries
            query = text("SELECT * FROM table WHERE id = :id")
            result = db.session.execute(query, {'id': data['id']})
            # Process result...

        return make_response(result_data, 'Success message')
    except Exception as e:
        db.session.rollback()  # If modifying data
        return make_response(None, f'Error: {str(e)}', 500)
```

2. Add TypeScript API function in appropriate frontend `api/` file:
```typescript
export const functionName = async (params): Promise<ReturnType> => {
  try {
    const response = await axiosInstance.post('/endpoint', params)
    return response.data
  } catch (error) {
    console.error('Operation failed:', error)
    throw error
  }
}
```

3. Call from Vue component:
```typescript
import { functionName } from '@/api/moduleApi'

const handleAction = async () => {
  try {
    const result = await functionName(params)
    ElMessage.success('Success!')
  } catch (error) {
    ElMessage.error('Failed!')
  }
}
```

### Working with database queries

Always use parameterized queries with SQLAlchemy `text()`:
```python
# ✅ Correct - prevents SQL injection
query = text("SELECT * FROM users WHERE username = :username")
result = db.session.execute(query, {'username': username})

# ❌ Wrong - vulnerable to SQL injection
query = text(f"SELECT * FROM users WHERE username = '{username}'")
```

For INSERT/UPDATE/DELETE operations:
```python
try:
    query = text("INSERT INTO table (col1, col2) VALUES (:val1, :val2)")
    db.session.execute(query, {'val1': value1, 'val2': value2})
    db.session.commit()  # Must commit for changes
except Exception as e:
    db.session.rollback()  # Rollback on error
    raise e
```

### Element Plus usage

Both frontends use Element Plus UI library:
- Import components: `import { ElMessage, ElMessageBox } from 'element-plus'`
- Use globally registered components in templates: `<el-button>`, `<el-table>`, etc.
- Common patterns in this codebase:
  - `ElMessage.success()` / `ElMessage.error()` for notifications
  - `ElMessageBox.confirm()` for confirmation dialogs
  - `<el-table>` with `<el-table-column>` for data tables
  - `<el-form>` with validation rules

## Important Notes

### Security Issues (Current Implementation)

⚠️ **The following security issues exist and should be addressed before production:**

1. **Password storage**: Passwords stored in plain text (should use bcrypt)
2. **Token validation**: Mock tokens not validated by backend
3. **CORS**: No CORS configuration (may cause issues with different origins)
4. **SQL injection**: While using parameterized queries, still be cautious
5. **`.env` file**: Contains credentials, ensure it's in `.gitignore`

### Backend-Specific Behaviors

- **User ID reindexing**: When deleting a user, all subsequent user IDs are renumbered sequentially. This is intentional but unusual.
- **Book ID gap filling**: When adding a book, the system finds the smallest unused ID (e.g., if IDs are 1,2,4,5, new book gets ID 3)
- **Book deletion**: Does NOT reindex IDs like user deletion does
- **Database views**: Backend queries books directly with JOINs instead of using the `v_book_with_category` view

### Frontend-Specific Behaviors

- **Admin auth check**: Happens on every route navigation, checks both login status AND admin role
- **LocalStorage keys**: `token`, `username`, `role`, `isLoggedIn` - clear all four on logout
- **API responses**: Always check `response.code === 200` before accessing `response.data`
- **Port configuration**: Admin frontend uses port 5173, public system may use 5174 or another port

## Database Maintenance

The `mysql_database.sql` file includes sample data with:
- 1 admin user (username: `admin`, password: see SQL comments)
- 10 book categories
- 50+ sample books across all categories
- Pre-configured permissions and role mappings

When making schema changes:
1. Update `mysql_database.sql` with new DDL
2. Update backend `app.py` queries accordingly
3. Update frontend TypeScript interfaces to match
4. Test with existing data to ensure no breaking changes
