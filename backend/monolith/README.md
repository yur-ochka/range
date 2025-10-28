# Monolith backend skeleton

This folder contains the new monolithic Django project skeleton.

What’s included:
- core/settings.py: DRF, CORS, env-based config, SQLite by default
- core/urls.py, asgi.py, wsgi.py
- manage.py (DJANGO_SETTINGS_MODULE=core.settings)
- .env.example
- apps/: place to move domain apps here (accounts, catalog, cart, order, payment, review)

Quick start:
1. Create .env from .env.example and adjust values
2. Install dependencies (use your existing backend/requirements.txt or a dedicated monolith one)
3. Run migrations and start server:
   - python manage.py migrate
   - python manage.py createsuperuser
   - python manage.py runserver

Notes:
- Add your local apps under apps/ and register them in INSTALLED_APPS
- Set AUTH_USER_MODEL if you migrate a custom user model
- Update CORS and REST_FRAMEWORK settings as needed
