# Payment Integrations Notes

- PayTabs / Tap / HyperPay are popular in MENA and KSA.
- Recommended approach:
  - Use server-side SDK or HTTP API to create payment sessions or tokens.
  - Implement webhook endpoint to receive payment success/cancellation events and verify signatures.
  - Store minimal payment metadata and generate receipts on payment success.

- Environment variables:
  - PAYTABS_SECRET
  - TAP_SECRET
  - HYPERPAY_SECRET
