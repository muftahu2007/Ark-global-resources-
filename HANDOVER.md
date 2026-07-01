# Ark Global Resources - Handover Document

Welcome to the Ark Global Resources application! This document provides all the essential information you (or future developers) will need to run, test, and deploy this Django project. Keep this document secure and **never commit your `.env` file to version control**.

---

## 1. Local Setup Instructions

To get the application running locally on your machine, follow these steps:

1. **Clone the repository** to your local machine.
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables (`.env`)**

   Create a `.env` file in the root directory (where `manage.py` lives). Do **not** commit this file to version control!

   ```env
   # Core Django
   DEBUG=True
   SECRET_KEY=your-very-long-random-secret-key-here

   # Database (Supabase - Transaction Pooler Port 6543)
   DATABASE_URL=postgresql://USER:PASSWORD@HOST:6543/postgres

   # Media Storage
   CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

   # Business Configuration
   WHATSAPP_NUMBER=2348071062530
   ARK_EXECUTIVE_EMAIL=executive@arkglobalresources.com

   # Email (Gmail SMTP)
   EMAIL_HOST_USER=your-smtp-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   DEFAULT_FROM_EMAIL=noreply@arkglobalresources.com

   # Security - Custom Admin Door
   SECRET_ADMIN_PATH=your-secret-admin-url-slug
   SECRET_ADMIN_KEY=YourStrongAdminPassphrase2026
   ```

   > **Note on `SECRET_ADMIN_PATH` and `SECRET_ADMIN_KEY`:** These protect the real Django admin panel. The admin is accessible at `yourdomain.com/<SECRET_ADMIN_PATH>/`. You must enter the `SECRET_ADMIN_KEY` as a passphrase before the admin login appears. Keep these values private.

5. **Run Migrations and Create the Cache Table:**
   ```bash
   python manage.py migrate
   python manage.py createcachetable
   ```

6. **Create the Superuser (First-Time Setup Only):**
   ```bash
   python manage.py createsuperuser
   ```
   This account is what you use to log into the CEO portal and the hidden admin panel.

7. **Collect Static Files (for local production testing):**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the Server:**
   ```bash
   python manage.py runserver
   ```

---

## 2. Running the Test Suite

The project uses `pytest` and `coverage` to automatically verify that the codebase is functioning correctly and hasn't been broken by recent changes.

To run the test suite and check code coverage:
```bash
coverage run -m pytest
coverage report -m
```

> **Note:** A `conftest.py` file is included which safely forces the test suite to use a fast, in-memory SQLite database and disables SSL redirects so tests run instantly and securely without touching your production database.

**Current Coverage:** The test suite currently covers **79%** of the codebase, which is an excellent metric for a project of this scale.

---

## 3. Deployment — Render (Primary / Recommended)

**Render is the recommended production platform** for this application. It supports persistent server processes, which is required to run the Django-Q background task worker (`qcluster`).

All Render configuration files are already included:

| File | Purpose |
|---|---|
| `Procfile` | Tells Render how to start the app (`bash start.sh`) |
| `build.sh` | Runs `pip install`, `collectstatic`, `migrate`, and `createcachetable` on each deploy |
| `start.sh` | Starts the Django-Q background worker AND Gunicorn web server |

### Steps to Deploy on Render

1. Push the repository to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service** → Connect your GitHub repo.
3. Set the following in **Build & Deploy Settings**:
   - **Build Command:** `./build.sh`
   - **Start Command:** `bash start.sh`
4. Under **Environment Variables**, add all keys from your `.env` file above, plus:
   ```
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com,www.arkglobalresources.com
   ```
5. Click **Deploy** and monitor the build logs.

---

## 4. Deployment — Vercel (Alternative / Limited)

A `vercel.json` is included for optional Vercel deployment. However, **Vercel is a serverless platform** and has the following critical limitations with this app:

| Feature | Render | Vercel |
|---|---|---|
| Gunicorn web server | ✅ Full support | ✅ Supported via WSGI adapter |
| Django-Q background worker | ✅ Runs persistently | ❌ Not supported (serverless) |
| File system writes | ✅ Writable | ❌ Read-only filesystem |
| Long-running processes | ✅ Supported | ❌ 10s max execution time |

**If deploying to Vercel:**
- Background tasks via Django-Q **will not run**. Any scheduled or async task will silently fail.
- All media uploads **must** route through Cloudinary. Do not attempt local file writes.
- Set `DEBUG=False` in Vercel's Environment Variables.
- Set `SECURE_SSL_REDIRECT=False` in Vercel's Environment Variables (Vercel handles HTTPS termination automatically — double-redirecting causes a redirect loop).

---

## 5. Pushing to Both Render and Vercel Simultaneously

Both platforms watch your GitHub repository and auto-deploy on push. To deploy to both at the same time:

1. Make sure your repo is connected to both Render and Vercel dashboards.
2. Simply push to your main branch:
   ```bash
   git add .
   git commit -m "your commit message"
   git push origin main
   ```
3. Both platforms will automatically detect the push and trigger their build pipelines simultaneously.

> **Tip:** You can monitor both deployments in parallel — Render dashboard and Vercel dashboard — in separate browser tabs.

---

## 6. Security & Deployment Warnings (Pre-Launch Checklist)

Running Django's deployment check (`python manage.py check --deploy`) flags the following security items. These are intentionally inactive locally but **must** be confirmed in production:

| # | Setting | Status in Production |
|---|---|---|
| 1 | `DEBUG=False` | ✅ Auto-resolved by setting `DEBUG=False` in env vars |
| 2 | `SECURE_SSL_REDIRECT=True` | ✅ Auto-activated when `DEBUG=False` (set to `False` on Vercel only) |
| 3 | `SESSION_COOKIE_SECURE=True` | ✅ Auto-activated when `DEBUG=False` |
| 4 | `CSRF_COOKIE_SECURE=True` | ✅ Auto-activated when `DEBUG=False` |
| 5 | `SECURE_HSTS_SECONDS` | ✅ Set to 1 year (31536000) when `DEBUG=False` |

### Additional Security Notes
- The **real Django admin** is hidden at `/<SECRET_ADMIN_PATH>/admin/`. The standard `/admin/` URL leads to a decoy login page that logs all intrusion attempts to the CEO portal's threat intelligence console.
- The **Gatekeeper middleware** enforces cookie-based access to the admin door. Do not remove `GatekeeperMiddleware` from `MIDDLEWARE` in `settings.py`.
- **Cloudinary credentials** are set via the `CLOUDINARY_URL` environment variable. Ensure this is always set in production to prevent fallback to any hardcoded values.

---

## 7. Known Limitations

- **Background Tasks on Vercel:** Because Vercel is serverless, the Django-Q worker (`qcluster`) cannot run natively. Use Render if background task execution is required.
- **Database Connection Pooling:** Both Render and Vercel may spin up multiple concurrent instances. Always use the **Transaction connection pooler** URL from Supabase (port `6543`), not the direct connection (port `5432`). The app is already configured with `conn_max_age=0` to handle this correctly.
- **Large File Uploads:** The app is configured to accept up to 250MB per request and up to 5,000 files per bulk upload. Ensure your hosting tier supports this traffic volume.
- **Email on Vercel:** SMTP calls (Gmail) may time out on Vercel's serverless functions. Render is recommended if reliable transactional email is required.

---

## 8. Project Architecture Overview

```
ark_global resource/
├── global_ark/          # Django project config (settings, urls, wsgi)
├── ark_catalog/         # Public-facing catalog app (fleet, sourcing, inquiries)
├── ceo_portal/          # Private CEO dashboard (analytics, asset management, security)
├── templates/           # Global HTML templates (emails, base layouts)
├── static/              # CSS, JS, images (served via WhiteNoise)
├── staticfiles/         # Compiled static files for production (auto-generated)
├── Procfile             # Render process configuration
├── build.sh             # Render build script
├── start.sh             # Gunicorn + Django-Q startup script
├── vercel.json          # Vercel serverless routing configuration
├── requirements.txt     # Python dependencies  
└── conftest.py          # Pytest configuration (in-memory DB, no SSL)
```

---

*Last updated: July 2026 | Prepared by: Ark Global Resources Development Team*
