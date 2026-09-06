# Production readiness checklist

Use this checklist before promoting a release.

## Access and deployment

- [ ] `staging` and `production` GitHub Environments have required approvers.
- [ ] SSH host keys are pinned or verified outside the workflow.
- [ ] `STAGING_*` and `PRODUCTION_*` secrets are configured.
- [ ] The target host has Docker Compose, curl, DNS, and ports 80/443 ready.
- [ ] `.env.production` and `secrets/allowed_api_keys` exist only on the target host.
- [ ] The deployed `IMAGE_TAG` is immutable and was validated in staging.

## Security

- [ ] API keys use file permissions 400 or 600.
- [ ] Anonymous requests are disabled.
- [ ] CORS contains only approved origins.
- [ ] TLS certificate issuance and renewal succeed.
- [ ] No secret appears in workflow logs or uploaded artifacts.

## Reliability

- [ ] `/health/live` returns 200.
- [ ] `/health/ready` returns 200 with the expected model available.
- [ ] Authenticated `/v1/models` returns 200.
- [ ] Provider fallback behavior has been verified.
- [ ] Rollback was tested in staging and the previous tag is recorded.

## Performance and observability

- [ ] Health benchmark report is attached to the release.
- [ ] Inference benchmark report includes throughput, p95/p99, streaming first byte, and memory.
- [ ] Prometheus targets and alerts are healthy.
- [ ] OpenTelemetry traces reach the collector and backend.
- [ ] Logs, metrics, and traces can be correlated by `X-Request-Id`.

## Approval

- Release tag:
- Image digest:
- Staging validation run:
- Production validation run:
- Rollback owner:
- Approval:
