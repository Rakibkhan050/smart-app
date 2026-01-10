# School SaaS — MVP Scaffold

This repository contains a scaffold for a Student Management SaaS MVP.

## Structure
- backend/ — Django 4.x project (`school_saas`) with apps `users`, `tenants`, `notifications`, `payments`, `receipts`.
- frontend/ — Next.js (TypeScript) app with Tailwind and i18n (English + Arabic)
- mobile/ — placeholder for Flutter app notes

## Quick start (PowerShell)
1. Copy environment example:
   cp .env.example .env
2. Start services with Docker Compose:
   docker compose up --build
3. Run migrations and create superuser:
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
4. Run tests locally:
   cd backend
   pytest

## Notes
- Add your `SENDGRID_API_KEY`, `AWS_*` credentials and payment provider keys to `.env`.
- For web push, set `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY`.

## Next steps
- Implement multi-tenant middleware or schema strategy
- Wire up payment provider integrations and webhooks
- Add client-side Auth and JWT endpoints

