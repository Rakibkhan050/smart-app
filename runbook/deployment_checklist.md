# Deployment Checklist

- [ ] Ensure `DATABASE_URL`, `REDIS_URL`, `AWS_*` env vars are set
- [ ] Run migrations and collectstatic
- [ ] Configure monitoring and alerts
- [ ] Verify SendGrid and payment provider credentials
- [ ] Verify VAPID keys for web push and `NEXT_PUBLIC_VAPID_PUBLIC_KEY` is set for frontend
- [ ] Verify Celery worker is running and can access Redis
- [ ] Verify S3 credentials and that uploads generate accessible presigned URLs

# Saudi market notes
- VAT must be applied according to local laws; ensure invoice templates show VAT breakdown.
- Consider PayTabs / Tap / HyperPay integrations for local payments; verify onboarding and test modes.
- For payments, ensure you verify webhook signatures and handle refunds/local tax reporting as required.
