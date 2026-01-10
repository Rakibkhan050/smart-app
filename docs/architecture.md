# Architecture Overview

## Multi-tenant approach
- Simple tenant scoping using a `tenant_id` field on shared models.
- For production, consider schema-per-tenant (Postgres schemas) or fully isolated DBs for larger tenants.

## Components
- Backend: Django + DRF, Channels for realtime, Celery for background tasks.
- Frontend: Next.js (TypeScript) with Tailwind CSS and next-i18next for i18n (English + Arabic RTL)
- Storage: S3-compatible for receipts and uploaded assets
- DB: PostgreSQL (managed RDS recommended)
- Cache / Broker: Redis (channels + Celery)

## Deployment recommendations
- Use managed services for DB and Redis (AWS RDS / Elasticache, DigitalOcean Managed DB/Redis).
- Use a container registry + CI for image builds; use k8s or Docker Compose for orchestration depending on scale.
