# START HERE — Healthcare assignment, next-day submission

**What you have:** Complete Django project scaffold with 4 required API sections, PostgreSQL configuration, JWT auth, 9 automated test methods, a Postman collection of 17 requests, and a detailed README. **What you still must do:** install locally, set PostgreSQL credentials, run migrations, test on PostgreSQL, and check your submission. Use fictitious medical data only.

## A. Get the code running (Windows PowerShell)

1. Extract the ZIP. Open the inner `healthcare_django_starter` folder in VS Code. Use `Terminal -> New Terminal` (PowerShell).
2. Verify Python: `py --version`. Python 3.12 or 3.13 is recommended.
3. Run the following commands ONE AT A TIME inside the project folder. Using the venv's Python directly avoids PowerShell activation-policy problems.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy the generated random secret from the last command.

## B. Configure PostgreSQL (do not substitute SQLite in the final app)

Install PostgreSQL and pgAdmin if needed: https://www.postgresql.org/download/windows/ . In pgAdmin, connect to your local PostgreSQL instance, open the Query Tool on the default `postgres` database and run these SQL statements **separately**. Choose your OWN strong password; don't use the example literally.

```sql
CREATE USER healthcare_user WITH PASSWORD 'YOUR_OWN_STRONG_DB_PASSWORD';
```

```sql
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

Open the project `.env` file and set:

```ini
DJANGO_SECRET_KEY=PASTE_YOUR_RANDOM_SECRET_HERE
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=YOUR_OWN_STRONG_DB_PASSWORD
DB_HOST=127.0.0.1
DB_PORT=5432
```

This is for LOCAL development. **Never commit `.env` to GitHub.** The included `.gitignore` excludes it.

## C. Run the app

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

The server should run at `http://127.0.0.1:8000`. A `401 Unauthorized` from `GET /api/patients/` without a JWT is the correct security behavior. Leave this terminal running while you use Postman.

## D. Test in Postman (proof the assignment works)

1. Import `Healthcare_Assignment.postman_collection.json` into Postman.
2. Run its requests numbered **01 to 17 in order**. Register runs only once per email. Login automatically saves the JWT; creation requests automatically save patient/doctor/mapping IDs.
3. Key success responses to confirm: register **201**; login **200** with `access` + `refresh`; create patient **201**; create doctor **201**; map doctor to patient **201**; GET the mappings **200**; update **200**; delete **204**.
4. Also verify failures: an unauthenticated GET `/api/patients/` is **401**; invalid age 121 is **400**; duplicate mapping is **400**; a second user cannot read or edit the first user's patients (**404** for detail requests).
5. To demonstrate data really uses PostgreSQL, inspect `healthcare_db` in pgAdmin. Under `Schemas > public > Tables`, look for `clinic_patient`, `clinic_doctor`, and `clinic_patientdoctormapping`. If you deleted your demo records in Postman, create another demo record before checking.

## E. Automated tests and hand-in

Run the quick automated test suite (uses SQLite **only for isolated tests**, not your actual app):

```powershell
.\.venv\Scripts\python.exe manage.py test --settings=healthcare_backend.test_settings
```

This project has 9 test methods; verify the output says `OK` on your laptop. The real app's `.env` configuration uses PostgreSQL. You can also run PostgreSQL-backed tests with `python manage.py test`, but the DB role needs permission to create a temporary test database; manually testing the real PostgreSQL app via Postman is essential regardless.

**Before submitting:** check the recruiter requested format and deadline; include the source code, `requirements.txt`, `.env.example`, initial migrations, README and Postman collection. Do not include `.env`, `.venv`, JWTs, passwords or real patient data. If asked for a GitHub link, commit the files from `healthcare_django_starter` to a new repository. Avoid saying tests passed unless you actually ran them.

## What to understand for the interview

- `accounts/serializers.py`: registration validation and `create_user()` password hashing.
- `accounts/views.py`: email/password login and JWT generation.
- `clinic/models.py`: PostgreSQL tables and foreign keys.
- `clinic/serializers.py`: JSON validation and protection against assigning someone else's patient.
- `clinic/views.py`: patient ownership filtering with `get_queryset()`; doctor CRUD; mapping logic.
- `clinic/permissions.py`: any authenticated user can read doctors; only their creator can edit/delete.
- `healthcare_backend/settings.py`: PostgreSQL connection, JWT and `.env` settings.

**One assignment-specific detail:** `GET /api/mappings/<number>/` treats the number as a **patient ID**. `DELETE /api/mappings/<number>/` treats it as a **mapping ID**. This is how the assignment defines the endpoints; the HTTP method distinguishes their meaning.

## If something fails

- `py` not found: install Python from https://www.python.org/downloads/windows/ and enable PATH, then reopen PowerShell.
- `No module named django`: rerun pip install using the SAME `./.venv/Scripts/python.exe` interpreter shown above.
- `password authentication failed for user`: compare `DB_USER` and `DB_PASSWORD` in `.env` against your PostgreSQL role.
- `connection refused`: ensure PostgreSQL is running and the port matches `.env` (default 5432).
- `database does not exist`: create `healthcare_db` in pgAdmin, then rerun `migrate`.
- `401` on a protected request: log in, check the Postman collection stored `access_token` and use `Authorization: Bearer <access_token>`.
- `400` on mapping creation: check the IDs are valid, the patient belongs to you, and the mapping does not already exist.

For a comprehensive explanation of each endpoint and the full Windows setup, read `README.md`.
