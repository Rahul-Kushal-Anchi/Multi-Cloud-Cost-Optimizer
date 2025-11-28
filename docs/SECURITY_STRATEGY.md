# Security Strategy

## Infrastructure Security

### Docker Base Image
- Using `python:3.11-slim-bookworm` (latest Debian)
- Running `apt-get upgrade` for security patches
- Monthly rebuild to get latest updates

### Container Hardening
- Non-root execution (appuser:1000)
- Minimal packages installed
- Regular Trivy scans

## Application Security

### Python Dependencies
- starlette ≥0.40.0 (DoS fix)
- python-jose ≥3.3.0 (algorithm fix)
- ecdsa ≥0.19.0 (Minerva attack fix)

### AWS Security
- IAM cross-account roles
- Read-only permissions
- No data storage

## Monitoring
- GitHub Security scanning
- Automated dependency updates
