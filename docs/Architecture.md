# Architecture Overview

```
+------------+        HTTPS         +----------------------+        Internal         +------------------+
|  Browser   |  ─────────────────►  |  AWS ALB (public)   |  ─────────────────────►  |  ECS Fargate     |
|  (tenant & |                     |  Path-based routing  |                          |  Services        |
|  owner UI) |                     |                      |                          |                  |
+------------+                     +----------------------+                          +---------+--------+
                                                                                            │
                                           ┌────────────────────────────────────────────────┴──────────────────┐
                                           │                                                                   │
                                   +-------▼--------+                                               +---------▼----------+
                                   | Web container  |  Serves React SPA (build from `web-app/`)    | API container      |
                                   | (Nginx/Node)   |  Assets pulled from same ECS service         | FastAPI (`api/`)   |
                                   +----------------+                                               +---------+----------+
                                                                                                             │
                                                                                                             │SQLModel ORM
                                                                                                             │(RDS/Postgres)
                                                                                                             ▼
                                                                                                    +----------------------+
                                                                                                    |   Application DB     |
                                                                                                    |   (multi-tenant)     |
                                                                                                    +----------+-----------+
                                                                                                               │
                                                                                                   Stores tenant profiles,
                                                                                                   users, invites, AWS
                                                                                                   connection metadata.
```

## AWS Cost Data Flow

1. **Tenant connection** (Connect AWS page)
   - Tenant owner submits the Cross-Account `Role ARN`, `ExternalId`, CUR bucket, Athena details.
   - FastAPI service uses `sts:AssumeRole` to validate the trust relationship and stores the metadata (encrypted) against the tenant row.

2. **Requesting cost analytics**
   - Frontend requests endpoints such as `/api/costs?days=7`, `/api/dashboard`, `/api/costs/trends` with a JWT.
   - FastAPI resolves the tenant from the JWT, pulls the saved AWS connection settings, and assumes the customer role.
   - Using the temporary credentials, the service queries Amazon Athena (backed by the customer's CUR in S3) and returns aggregated cost data.

3. **Multi-tenant isolation**
   - JWTs include `user_id`, `tenant_id`, and `role` (`global_owner`, `owner`, `admin`, `member`).
   - Database rows are keyed by tenant and filtered through SQLModel dependencies to prevent cross-tenant access.
   - Global owner routes (under `/api/admin`) require the `global_owner` role.

## Supporting AWS Resources

- **ECS/Fargate services** for both web and API containers.
- **Application Load Balancer** with path-based routing (`/api/*` → API task, others → Web task).
- **AWS Systems Manager Parameter Store / Secrets Manager** for secrets such as `APP_JWT_SECRET`.
- **Amazon RDS (PostgreSQL)** or compatible SQL database for persistent tenant metadata.
- **Amazon S3 + AWS Cost and Usage Report (CUR)** for raw billing data per tenant.
- **AWS Glue + Amazon Athena** for SQL access to each tenant's CUR.
- **Amazon SNS (optional)** for CUR arrival notifications.

This repository contains:
- `web-app/` – React frontend.
- `api/` – FastAPI backend.
- `infra/` – Terraform modules/resources for core AWS infrastructure.
- `cfn/connect-aws-billing.yml` – CloudFormation template customers deploy in their own AWS account to grant read-only access.
- `build_and_deploy.sh` – Script to build Docker images, push to ECR, and trigger an ECS rolling update.

