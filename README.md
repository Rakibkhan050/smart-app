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

## Auth & Web Push
- The backend exposes JWT endpoints at `/api/auth/token/` and `/api/auth/token/refresh/` and `/api/auth/register/`.
- Set `NEXT_PUBLIC_API_BASE` in your `.env` to point the frontend to the backend API (default http://localhost:8000/api/).
- For web-push, set `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY` (server) and `NEXT_PUBLIC_VAPID_PUBLIC_KEY` for the frontend. Use the Notifications page to register service worker and send a demo subscription to the server.

## Payments
- Payment provider secrets (PayTabs/Tap/HyperPay) go into `.env` (`PAYTABS_SECRET`, `TAP_SECRET`, `HYPERPAY_SECRET`).
- The `/api/payments/create-intent/` endpoint returns a mock session for local testing. The `/api/payments/webhook/` endpoint validates signatures using HMAC-based checks and enqueues a Celery task to generate receipts when valid.
- For local testing, use `/api/payments/test-webhook/` (authenticated) to simulate a payment webhook and trigger receipt generation without signing.

## Notes
- Add your `SENDGRID_API_KEY`, `AWS_*` credentials and payment provider keys to `.env`.
- For web push, set `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY`.

## Next steps
- Implement multi-tenant middleware or schema strategy
- Wire up payment provider integrations and webhooks
- Add client-side Auth and JWT endpoints

