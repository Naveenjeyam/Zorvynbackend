# Finance Dashboard Backend

A Django REST Framework backend for a role-based finance dashboard system.
Supports financial record management, user roles, access control, and analytics APIs.

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Framework    | Django 4.2 + Django REST Framework  |
| Database     | MySQL                               |
| Auth         | JWT via `djangorestframework-simplejwt` |
| Filtering    | `django-filter`                     |
| API Docs     | Swagger UI via `drf-yasg`           |
| CORS         | `django-cors-headers`               |

---

## Project Structure

```
finance_backend/
├── core/                         # User model, auth, role management
│   ├── management/commands/
│   │   └── seed_data.py          # DB seeder
│   ├── models.py                 # Custom User model
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py            # Role-based permission classes
│   ├── urls.py
│   └── admin.py
├── finance/                      # Financial records & categories
│   ├── models.py                 # FinancialRecord (soft delete), Category
│   ├── serializers.py
│   ├── filters.py                # Advanced filtering
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── dashboard/                    # Analytics & summary APIs
│   ├── views.py
│   └── urls.py
├── finance_backend/              # Django project config
│   ├── settings.py
│   └── urls.py
├── requirements.txt
└── .env.example
```

---

## Setup Instructions

### 1. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd finance_backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

`.env` contents:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=finance_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
```

### 4. Create MySQL database

```sql
CREATE DATABASE finance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed initial data

```bash
python manage.py seed_data
```

This creates:
| User    | Email                    | Password     | Role    |
|---------|--------------------------|--------------|---------|
| Admin   | admin@finance.com        | Admin@1234   | admin   |
| Analyst | analyst@finance.com      | Analyst@1234 | analyst |
| Viewer  | viewer@finance.com       | Viewer@1234  | viewer  |

Also seeds 10 categories and 60 sample financial records.

### 7. Run server

```bash
python manage.py runserver
```

---

## API Documentation

Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
ReDoc:       [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

---

## API Endpoints

### Authentication

| Method | Endpoint                        | Access  | Description                  |
|--------|---------------------------------|---------|------------------------------|
| POST   | /api/auth/register/             | Public  | Register new user (viewer)   |
| POST   | /api/auth/login/                | Public  | Login → get JWT tokens       |
| POST   | /api/auth/logout/               | Any     | Logout (blacklist token)     |
| GET    | /api/auth/profile/              | Any     | View own profile             |
| PUT    | /api/auth/profile/              | Any     | Update own name              |
| POST   | /api/auth/change-password/      | Any     | Change own password          |
| POST   | /api/auth/token/refresh/        | Public  | Refresh access token         |
| GET    | /api/auth/users/                | Admin   | List all users               |
| POST   | /api/auth/users/                | Admin   | Create user with any role    |
| GET    | /api/auth/users/<id>/           | Admin   | Get user details             |
| PUT    | /api/auth/users/<id>/           | Admin   | Update user role/status      |
| DELETE | /api/auth/users/<id>/           | Admin   | Deactivate user (soft)       |

### Financial Records

| Method | Endpoint                        | Access         | Description               |
|--------|---------------------------------|----------------|---------------------------|
| GET    | /api/finance/records/           | All roles      | List records with filters |
| POST   | /api/finance/records/           | Admin          | Create a record           |
| GET    | /api/finance/records/<id>/      | All roles      | View single record        |
| PUT    | /api/finance/records/<id>/      | Admin          | Update record             |
| PATCH  | /api/finance/records/<id>/      | Admin          | Partial update            |
| DELETE | /api/finance/records/<id>/      | Admin          | Soft delete record        |

**Record Filters (query params):**
```
?type=income|expense
?category=<id>
?date_from=YYYY-MM-DD
?date_to=YYYY-MM-DD
?amount_min=100
?amount_max=5000
?month=1-12
?year=2024
?search=<text>          (searches notes and category name)
?ordering=date|-date|amount|-amount
?page=1&page_size=10
```

### Categories

| Method | Endpoint                        | Access    | Description          |
|--------|---------------------------------|-----------|----------------------|
| GET    | /api/finance/categories/        | All roles | List all categories  |
| POST   | /api/finance/categories/        | Admin     | Create category      |
| GET    | /api/finance/categories/<id>/   | All roles | View category        |
| PUT    | /api/finance/categories/<id>/   | Admin     | Update category      |
| DELETE | /api/finance/categories/<id>/   | Admin     | Delete category      |

### Dashboard Analytics

| Method | Endpoint                           | Access          | Description                    |
|--------|------------------------------------|-----------------|--------------------------------|
| GET    | /api/dashboard/summary/            | All roles       | Total income, expense, balance |
| GET    | /api/dashboard/recent-activity/    | All roles       | Latest N transactions          |
| GET    | /api/dashboard/category-breakdown/ | Analyst + Admin | Totals grouped by category     |
| GET    | /api/dashboard/monthly-trend/      | Analyst + Admin | Monthly income/expense trend   |
| GET    | /api/dashboard/weekly-trend/       | Analyst + Admin | Weekly trend (last 8 weeks)    |

**Dashboard filter params:**
```
/api/dashboard/summary/?year=2024
/api/dashboard/category-breakdown/?type=expense&year=2024&month=6
/api/dashboard/monthly-trend/?year=2024
/api/dashboard/recent-activity/?limit=20
```

---

## Role Access Matrix

| Action                        | Viewer | Analyst | Admin |
|-------------------------------|--------|---------|-------|
| Register / Login              | ✅     | ✅      | ✅    |
| View own profile              | ✅     | ✅      | ✅    |
| View financial records        | ✅     | ✅      | ✅    |
| View categories               | ✅     | ✅      | ✅    |
| View summary & recent activity| ✅     | ✅      | ✅    |
| View category breakdown       | ❌     | ✅      | ✅    |
| View monthly/weekly trends    | ❌     | ✅      | ✅    |
| Create/Update/Delete records  | ❌     | ❌      | ✅    |
| Create/Update categories      | ❌     | ❌      | ✅    |
| Manage users                  | ❌     | ❌      | ✅    |

---

## Authentication Flow

```
1. POST /api/auth/login/  →  { access: "...", refresh: "..." }

2. Include in all subsequent requests:
   Header: Authorization: Bearer <access_token>

3. When access token expires (1 hour):
   POST /api/auth/token/refresh/  →  { access: "new_token" }

4. Logout:
   POST /api/auth/logout/  with body: { "refresh": "<refresh_token>" }
```

---

## Assumptions Made

1. **Public registration** creates Viewer role only. Admins create Analyst/Admin users via the `/api/auth/users/` endpoint.
2. **Soft delete** is used for both records and user deactivation. Data is never permanently removed via API.
3. **Amount is always positive** — the `type` field (income/expense) determines the direction.
4. **Pagination** defaults to 10 records per page. Override with `?page_size=N`.
5. **JWT tokens**: Access = 1 hour, Refresh = 7 days with rotation enabled.
6. **Categories** are shared system-wide, not per-user.

---

## Design Decisions

- **Custom User model** (`core.User`) extends `AbstractBaseUser` for full control over auth fields.
- **Permission classes** (`IsAdmin`, `IsAnalystOrAdmin`, `IsAnyRole`) are centralized in `core/permissions.py` and reused across apps.
- **Soft delete** is implemented at the model level with a `SoftDeleteManager` that automatically filters out deleted records.
- **Dashboard views** use Django ORM aggregations (`Sum`, `Count`, `TruncMonth`) for efficient analytics queries — no raw SQL.
- **Filters** use `django-filter` for clean, declarative filtering without messy manual querystring parsing.
