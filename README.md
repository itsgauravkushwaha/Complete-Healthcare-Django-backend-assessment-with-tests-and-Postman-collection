# Healthcare Backend — Beginner Django Assessment

This project implements all 4 sections of the assignment: JWT register/login, patient CRUD, doctor CRUD, and patient–doctor mappings. Built with Django 5.2 LTS, Django REST Framework, Simple JWT, and PostgreSQL. **Only use invented demo patients; this tutorial is not production healthcare software.**

## 1. Prerequisites (Windows PowerShell)

- Install Python **3.12 or 3.13** from https://www.python.org/downloads/ and select “Add Python to PATH”.
- Install **PostgreSQL 14+** and pgAdmin from https://www.postgresql.org/download/windows/; remember the `postgres` password set during installation.
- Install VS Code and Postman (or use VS Code's Thunder Client).
- Extract ZIP, open `healthcare_django_starter` in VS Code, and open a new **PowerShell** terminal from `Terminal > New Terminal`.

Verify Python:

```powershell
py --version
```

Make a virtual environment (local independent Python packages):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, either run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (only this terminal) and activate again, or **skip activation** and run `.\.venv\Scripts\python.exe` instead of `python` for commands below.

## 2. Create a PostgreSQL database

In pgAdmin: connect to your local PostgreSQL server; open **Query Tool** connected to the default `postgres` database. Run the following SQL, replacing the illustrative password with your own:

```sql
CREATE USER healthcare_user WITH PASSWORD 'choose_your_own_strong_password';
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

Run each line separately if your pgAdmin version disallows `CREATE DATABASE` in the same query execution.

## 3. Environment variables

Copy `.env.example` to `.env` (PowerShell):

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Edit `.env` in VS Code. Replace `DJANGO_SECRET_KEY` with that random output and `DB_PASSWORD` with the database password chosen above. **Do not put `.env` in GitHub, reports, or screenshots.** `.gitignore` already excludes it.

## 4. Make tables and start the server

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/api/patients/` in a browser. A 401 Unauthorized response is **good**: the endpoint is protected. Use Postman for the following steps. Keep the `runserver` terminal running.

**Vocabulary:** `models.py` defines database tables. `serializers.py` validates JSON input and converts database objects to JSON. `views.py` decides what happens for each request. `urls.py` matches URLs to the appropriate view. `migrations/` holds schema changes. The Django ORM lets you use Python instead of writing SQL for each request.

## 5. Postman test sequence

For the quickest walkthrough, **import** `Healthcare_Assignment.postman_collection.json` into Postman. Run requests **01 through 17 in order**. Login automatically saves your JWT and each create request saves its ID in collection variables. Registration works just once per email; if you already registered, skip request 01 or change the email in 01 and 02.

You can also test each endpoint manually using the examples below.

Set `Content-Type: application/json` for POST and PUT. Base URL is `http://127.0.0.1:8000`.

### Register (no auth)

`POST /api/auth/register/` JSON:

```json
{"name":"Gaurav","email":"gaurav@example.com","password":"StrongPass!2026"}
```

Expect **201 Created** and a user ID, name and email (never a password).

### Login (no auth)

`POST /api/auth/login/` JSON:

```json
{"email":"gaurav@example.com","password":"StrongPass!2026"}
```

Expect **200 OK** and `access` and `refresh` tokens. **In Postman > Authorization > Bearer Token**, paste the `access` token for every protected API below. Do not paste the `refresh` token there.

### Create a patient

`POST /api/patients/` JSON:

```json
{"name":"Demo Patient","age":32,"gender":"female","phone":"+919876543210"}
```

Expect 201; remember the returned patient `id` (example 1).

### Create a doctor

`POST /api/doctors/` JSON:

```json
{"name":"Dr. Meera Sharma","specialization":"Cardiology","email":"meera@example.com"}
```

Expect 201; remember the doctor `id` (example 1).

### Assign doctor to patient

`POST /api/mappings/` JSON, replacing the two IDs with actual values:

```json
{"patient":1,"doctor":1}
```

Expect 201; remember the returned **mapping id**. Next call `GET /api/mappings/` to see mapping records and `GET /api/mappings/1/` to list the doctors assigned to patient 1.

### Read/update/delete examples

- `GET /api/patients/` — your patients; `GET /api/patients/1/` — one of your patients.
- `PUT /api/patients/1/` — supply full patient JSON, including required `name` and `age`.
- `DELETE /api/patients/1/` — delete one of your patients. If it had assignments, they are deleted automatically.
- `GET /api/doctors/` and `GET /api/doctors/1/` — all doctor records / one doctor.
- `PUT /api/doctors/1/` — supply `name` and `specialization` (only if you created this doctor).
- `DELETE /api/doctors/1/` — delete a doctor you created.
- `DELETE /api/mappings/1/` — **the number is the mapping ID**, *not* the patient ID.

**Important route ambiguity inherited from the assessment:** In `GET /api/mappings/1/`, `1` means patient ID. In `DELETE /api/mappings/1/`, `1` means mapping ID. The project uses the HTTP method to distinguish them.

### Test negative cases

- GET `/api/patients/` without a token → **401**.
- POST `/api/patients/` with `age: 121` → **400**.
- Register the same email twice → **400**.
- Assign the same doctor to the same patient twice → **400**.
- Register a **second user** and log in with their token: they must see **none** of user 1's patients or mappings, cannot modify user 1's doctors, but can read the global doctor list.
- Try a nonexistent patient ID → **404**.

## 6. Automated tests

For an easy first run without configuring a test PostgreSQL user, run the provided isolated test suite against SQLite. You should see 9 tests and an `OK` result if everything is installed correctly:

```powershell
python manage.py test --settings=healthcare_backend.test_settings
```

**Important:** The assignment itself runs on PostgreSQL. The alternative SQLite setting is **only** for quick automated tests. For PostgreSQL integration tests, the database user must be permitted to create and drop a temporary test DB; then run `python manage.py test` using your `.env` PostgreSQL settings.

## 7. What each file does

- `accounts/serializers.py`: checks registration data and password strength; `create_user` stores a password hash.
- `accounts/views.py`: registers users, checks login and issues access/refresh JWTs.
- `clinic/models.py`: defines Patient, Doctor, PatientDoctorMapping; foreign keys and unique constraint make relationships reliable.
- `clinic/serializers.py`: accepts/validates API input; prevents mapping somebody else's patient; rejects duplicate assignments.
- `clinic/views.py`: REST CRUD, owner-based filtering, doctor object-level permissions and mapping operations.
- `clinic/urls.py`: DRF router automatically creates collection and item CRUD routes.
- `healthcare_backend/settings.py`: PostgreSQL, JWT, middleware and environment variables.
- `clinic/tests.py` and `accounts/tests.py`: sample API tests, including cross-user privacy cases.

## 8. Interview questions you should explain in your own words

1. **Django vs DRF?** Django provides the application framework and ORM. DRF makes REST API endpoints, serializers and authentication/permission handling easier.
2. **Model vs serializer vs view?** Model is schema/business relationships, serializer validates and converts data, view responds to HTTP requests.
3. **What is a foreign key?** A database link: one patient can have many doctor assignments; each mapping connects one patient to one doctor.
4. **Why JWT?** The client sends an access token on each protected request. A refresh token can request a fresh access token.
5. **Why ownership filtering?** `get_queryset()` limits patient results to `request.user`, including detail and deletion operations.
6. **Why `create_user()`?** It securely hashes passwords rather than storing them as plain text.
7. **What does `migrate` do?** It applies model-derived schema changes to a database.
8. **How do you prevent duplicate mappings?** Serializer validation provides a friendly 400 and a database `UniqueConstraint` preserves integrity.
9. **Why use `.env`?** To separate secret keys and database credentials from source code.
10. **How did you test?** Postman success/error cases and Django automated API tests, including two-account access checks. Only say you ran tests you actually ran.

## 9. Assessment design choices

- Email is stored in Django's unique built-in `username` field for a small assessment; it is also stored in the `email` field. A larger new application would generally use a custom email-based user model **before the first migration**.
- Doctor list/detail is visible to authenticated users, as requested, but editing/deleting a doctor is restricted to the person who created it.
- Mapping list is private to the user who owns the patients.
- This sample intentionally does not include production-grade consent workflows, audit logs, encrypted backups, deployment, or regulatory compliance. Never put real health records in it.
