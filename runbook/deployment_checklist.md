# Deployment Checklist

- [ ] Ensure `DATABASE_URL`, `REDIS_URL`, `AWS_*` env vars are set
- [ ] Run migrations and collectstatic
- [ ] Configure monitoring and alerts
- [ ] Verify SendGrid and payment provider credentials
- [ ] Verify VAPID keys for web push

# Saudi market notes
- VAT must be applied according to local laws; ensure invoice templates show VAT breakdown.
- Consider PayTabs / Tap / HyperPay integrations for local payments; verify onboarding and test modes.
