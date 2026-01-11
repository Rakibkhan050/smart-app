# Integration Testing with Stripe-mock and Moto

This guide explains how to run integration tests using local emulators instead of live APIs.

## Overview

- **stripe-mock**: Emulates Stripe API at `http://localhost:12111` (or `http://stripe-mock:12111` in Docker)
- **moto**: Emulates AWS S3 at `http://localhost:5000` (or `http://moto:5000` in Docker)

## Running Tests with Mock Services

### 1. Start Docker Compose with Mock Services

The docker-compose.yml now includes `stripe-mock` and `moto` services:

```bash
docker compose up -d stripe-mock moto
```

Or run everything (including backend, database, Redis):

```bash
docker compose up -d
```

### 2. Run Integration Tests

Enable mock mode and run tests:

```bash
# Option A: Run inside Docker container with mocks enabled
docker compose run --rm backend pytest payments/tests_stripe_mock.py receipts/tests_s3_mock.py -v

# Option B: Run locally (if backend dependencies installed) with env vars
export USE_STRIPE_MOCK=True
export USE_S3_MOCK=True
export STRIPE_MOCK_URL=http://localhost:12111
export AWS_S3_ENDPOINT_URL=http://localhost:5000
pytest payments/tests_stripe_mock.py receipts/tests_s3_mock.py -v
```

### 3. Run All Tests (Including Integration Tests)

```bash
docker compose run --rm backend pytest -v
```

Tests will automatically skip if mock services are unavailable:

```
test_stripe_mock_connection SKIPPED [stripe-mock Docker service not available]
test_moto_connection SKIPPED [moto Docker service not available]
```

## Environment Variables

### For Local Testing

Set these in your `.env` file:

```
# Enable mock services (default: False)
USE_STRIPE_MOCK=True
USE_S3_MOCK=True

# Mock service endpoints (these are the defaults)
STRIPE_MOCK_URL=http://localhost:12111
AWS_S3_ENDPOINT_URL=http://localhost:5000

# Still required but can be dummy values for mocks
STRIPE_API_KEY=sk_test_mock
STRIPE_WEBHOOK_SECRET=whsec_test_mock
AWS_ACCESS_KEY_ID=testing
AWS_SECRET_ACCESS_KEY=testing
AWS_STORAGE_BUCKET_NAME=test-bucket
```

### For Docker/CI

Environment variables are automatically set in `docker-compose.yml` and CI pipelines. When `USE_STRIPE_MOCK=True` or `USE_S3_MOCK=True`, the system will:

1. Configure Stripe client to hit `stripe-mock` Docker service
2. Configure boto3 to hit `moto` Docker service
3. Use test credentials instead of real API keys

## How It Works

### Stripe-mock Integration

- **File**: `backend/payments/adapters.py`
- **StripeAdapter** checks `USE_STRIPE_MOCK` setting
- If True: configures `stripe.api_base = 'http://stripe-mock:12111'`
- If False: uses real Stripe API with `STRIPE_API_KEY`
- Gracefully falls back to sandbox mode if mock unavailable

### S3 Moto Integration

- **File**: `backend/school_saas/settings.py`
- If `USE_S3_MOCK=True`: configures boto3 to hit moto server
- If False: uses real AWS S3 with credentials
- Tests can use moto as decorator (`@mock_s3`) or connect to Docker service

## Testing Workflow

### Example: Create Payment Intent via Stripe-mock

```bash
# Start services
docker compose up -d stripe-mock

# Run payment tests
docker compose run --rm backend pytest payments/tests_stripe_mock.py::StripeIntegrationTest::test_stripe_adapter_uses_mock -v
```

### Example: Create Receipt in S3 via Moto

```bash
# Start services
docker compose up -d moto

# Run receipt tests
docker compose run --rm backend pytest receipts/tests_s3_mock.py::S3IntegrationTest::test_receipt_s3_storage -v
```

## CI/CD Integration

In your CI pipeline (e.g., GitHub Actions), use:

```yaml
- name: Start mock services
  run: docker compose up -d stripe-mock moto

- name: Run integration tests
  run: docker compose run --rm backend pytest -v

- name: Stop mock services
  run: docker compose down
```

## Troubleshooting

### "stripe-mock Docker service not available"

This is expected if you haven't started the service. Tests will skip gracefully.

**Solution**: Run `docker compose up -d stripe-mock` before running tests.

### "Connection refused" when connecting to stripe-mock/moto

Ensure Docker Compose services are running:

```bash
docker compose ps

# You should see:
# stripe-mock   stripe/stripe-mock:latest   Up
# moto          motoapi/moto:latest         Up
```

### SSL/Certificate errors with moto

Moto uses HTTP (not HTTPS) by default. Ensure your S3 configuration uses `http://` not `https://`.

## Next Steps

After confirming mocks work locally:

1. ✅ Run unit tests with mocks: `pytest -m integration`
2. ✅ Run full suite: `pytest -v`
3. ✅ Add moto + stripe-mock to CI pipeline
4. 📝 Update docs with real payment flow examples
5. 🔐 Wire up real credentials for staging/production

## References

- [stripe-mock docs](https://github.com/stripe/stripe-mock)
- [moto docs](https://docs.getmoto.org/)
- [boto3 endpoint_url docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
