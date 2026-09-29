# Healthcare Management REST API

A RESTful healthcare backend developed using Django, Django REST Framework, and PostgreSQL. The application provides JWT-based authentication, patient and doctor management, and patient-doctor assignments with strict ownership-based access controls.

---

## Features

- **User Registration & JWT Authentication:** Secure signup and login issuing short-lived access tokens and refresh tokens via Simple JWT.
- **Patient Management (CRUD):** Complete record lifecycle for patient profiles with strict per-user data isolation.
- **Doctor Management (CRUD):** Directory of doctors searchable by authenticated users; update/delete restricted to the creating user.
- **Patient–Doctor Assignments:** Flexible mapping connecting patients with doctors, with built-in validation preventing duplicate assignments.
- **Ownership-Based Access Control:** Custom `get_queryset()` filtering ensures users can only read, update, or delete their own patients and mappings. Cross-user detail requests correctly return `404 Not Found`.
- **Input Validation & Error Handling:** Comprehensive field validation (e.g. realistic age boundaries, unique constraints, proper error formats).
- **Automated Testing Suite:** 9 unit and integration tests covering authentication, CRUD operations, permission guards, and relationship integrity.
- **Postman Collection Included:** 17 pre-configured requests with automated token storage and sequential testing flow.

---

## Tech Stack

- **Framework:** Django 5.2 LTS
- **API Toolkit:** Django REST Framework (DRF) 3.16+
- **Authentication:** `djangorestframework-simplejwt`
- **Database:** PostgreSQL (with `psycopg` 3)
- **Configuration:** `python-dotenv` for secure environment variable isolation

---

## Project Structure

```text
├── accounts/                                       # User registration, login, JWT views, and tests
├── clinic/                                         # Patient, Doctor, Mapping models, serializers, views, permissions, and tests
├── healthcare_backend/                             # Project settings, URL routing, WSGI/ASGI configuration
├── .env.example                                    # Sanitized environment variable template
├── .gitignore                                      # Excludes local secrets (.env), virtual environments (.venv), and caches
├── Healthcare_Assignment.postman_collection.json   # 17-request Postman test suite
├── manage.py                                       # Django CLI management script
├── README.md                                       # Project documentation
└── requirements.txt                                # Python package dependencies
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/itsgauravkushwaha/Complete-Healthcare-Django-backend-assessment-with-tests-and-Postman-collection.git
cd Complete-Healthcare-Django-backend-assessment-with-tests-and-Postman-collection
```

### 2. Create and Activate Virtual Environment

**Windows PowerShell:**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

*(If script execution is disabled in PowerShell, run `.\.venv\Scripts\python.exe` directly for all commands).*

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Configure PostgreSQL

1. Open pgAdmin or your PostgreSQL CLI.
2. Create the dedicated database user and database:

```sql
CREATE USER healthcare_user WITH PASSWORD 'choose_your_own_strong_password';
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

---

### 4. Environment Variables

Copy the template to create your local `.env` file:

```powershell
Copy-Item .env.example .env
```

Generate a secure Django secret key:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Edit `.env` and fill in your values:

```ini
DJANGO_SECRET_KEY=paste_generated_secret_key_here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=choose_your_own_strong_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

> **Security Note:** The `.env` file contains sensitive local credentials and is excluded from version control via `.gitignore`.

---

### 5. Apply Migrations & Start Server

Run database checks and apply migrations:

```powershell
python manage.py check
python manage.py migrate
```

Start the development server:

```powershell
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## API Reference

### Authentication (`/api/auth/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | No | Register a new user (`name`, `email`, `password`) |
| `POST` | `/api/auth/login/` | No | Authenticate user; returns `access` and `refresh` JWTs |

### Patients (`/api/patients/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/patients/` | Bearer Token | List all patients created by the authenticated user |
| `POST` | `/api/patients/` | Bearer Token | Create a patient record (`name`, `age`, `gender`, `phone`) |
| `GET` | `/api/patients/<id>/` | Bearer Token | Retrieve single patient (returns 404 if owned by another user) |
| `PUT` | `/api/patients/<id>/` | Bearer Token | Update patient details (restricted to owner) |
| `DELETE` | `/api/patients/<id>/` | Bearer Token | Delete patient record and related mappings (restricted to owner) |

### Doctors (`/api/doctors/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/doctors/` | Bearer Token | List all doctors in the directory |
| `POST` | `/api/doctors/` | Bearer Token | Add a new doctor (`name`, `specialization`, `email`) |
| `GET` | `/api/doctors/<id>/` | Bearer Token | Retrieve single doctor details |
| `PUT` | `/api/doctors/<id>/` | Bearer Token | Update doctor details (creator only) |
| `DELETE` | `/api/doctors/<id>/` | Bearer Token | Delete doctor record (creator only) |

### Mappings (`/api/mappings/`)

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/mappings/` | Bearer Token | List all mappings for the authenticated user's patients |
| `POST` | `/api/mappings/` | Bearer Token | Assign doctor to patient (`patient`, `doctor`) |
| `GET` | `/api/mappings/<patient_id>/` | Bearer Token | List doctors assigned to a specific patient ID |
| `DELETE` | `/api/mappings/<mapping_id>/` | Bearer Token | Remove a specific mapping by mapping ID |

---

## Testing

### Automated Test Suite

Run the automated test suite containing 9 test cases covering authentication, permissions, CRUD, and cross-user isolation:

```powershell
python manage.py test --settings=healthcare_backend.test_settings
```

Expected result:
```text
Ran 9 tests in 0.242s

OK
```

*(Note: `test_settings` uses an isolated in-memory SQLite database so tests can be run instantly and deterministically without altering your PostgreSQL data).*

### Postman Test Collection

1. Open Postman and click **Import**.
2. Select [`Healthcare_Assignment.postman_collection.json`](./Healthcare_Assignment.postman_collection.json).
3. Execute requests **01 through 17 in order**:
   - `01 - 02`: User registration and JWT login (saves JWT token to collection variable).
   - `03 - 07`: Patient creation, listing, retrieval, update, and boundary validation.
   - `08 - 10`: Doctor creation and listing.
   - `11 - 12`: Doctor assignment to patient and mapping retrieval.
   - `13 - 15`: Safe deletion of mappings, doctors, and patients.
   - `16 - 17`: Negative testing (invalid input validation and cross-user 404 security checks).

---

## Security & Architecture Highlights

1. **Password Security:** Handled using Django's `create_user()` method, which applies PBKDF2 with SHA-256 password hashing. Passwords are never stored or returned in plain text.
2. **Data Isolation (Tenant Separation):** Viewsets implement `get_queryset()` scoped strictly to `request.user`. Attempting to access another user's patient ID returns `404 Not Found` rather than `403 Forbidden`, preventing resource enumeration.
3. **Relationship Integrity:** Patient-doctor assignments enforce unique constraints at both serializer and database levels to prevent duplicate bookings. Foreign key cascades cleanly remove mappings when associated patient records are deleted.
