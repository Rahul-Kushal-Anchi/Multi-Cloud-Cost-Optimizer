# Architecture Overview

```
┌──────────────┐         ┌────────────────────┐         ┌──────────────────────────┐
│  Browser /   │  HTTPS  │  AWS ALB (public)  │  ┌─────▶│  ECS Service: Web (SPA)  │
│  React SPA   │────────▶│  Path-based routes │──┘      │  • Vite build + `serve`  │
└──────────────┘         └────────┬───────────┘         └──────────────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────────┐
                       │ ECS Service: API (FastAPI)│
                       │  • Auth & onboarding      │
                       │  • Settings, dashboards   │
                       │  • Tenant AWS integration │
                       └───────┬──────────┬───────┘
                               │          │
                               │          │ SQLModel ORM
                               │          ▼
                               │   ┌──────────────────────┐
                               │   │ PostgreSQL (RDS or   │
                               │   │ shared instance)     │
                               │   └─────────▲────────────┘
                               │             │
                               │   Stores tenants, users,
                               │   user settings, alerts,
                               │   AWS connection metadata.
                               │
                               ▼
                    sts:AssumeRole (ExternalId)
                               │
           ┌───────────────────┴──────────────────┐
           │                                      │
┌────────────────────────────┐        ┌────────────────────────────┐
│ Amazon Athena + S3 (CUR)   │        │ AWS Cost Explorer API      │
│ • Service cost breakdowns  │        │ • (Optional) additional    │
│ • Daily spend & trends     │        │   analytics                │
└────────────────────────────┘        └────────────────────────────┘
```

## AWS Cost Data Flow

1. **Tenant connection** (Connect AWS page)
   - Tenant owner submits the Cross-Account `Role ARN`, `ExternalId`, CUR bucket, Athena details.
   - FastAPI validates the trust relationship by calling `sts:AssumeRole` with the ExternalId and stores the metadata against the tenant row.

2. **Requesting cost analytics**
   - Frontend requests endpoints such as `/api/costs?days=7`, `/api/dashboard`, `/api/costs/trends` with a JWT.
   - FastAPI resolves the tenant from the JWT, pulls the saved AWS connection settings, and assumes the customer role.
   - Using the temporary credentials, the service queries Amazon Athena (backed by the customer's CUR in S3) and returns aggregated cost data.
   - The API returns quick stats, top services, alerts, and optimization hints to the React SPA. React Query keeps the UI in sync across pages (sidebar, dashboard, analytics).

3. **Multi-tenant isolation**
   - JWTs include `user_id`, `tenant_id`, and `role` (`global_owner`, `owner`, `admin`, `member`).
   - Database rows are keyed by tenant and filtered through SQLModel dependencies to prevent cross-tenant access.
   - Global owner routes (under `/api/admin`) require the `global_owner` role.

## Supporting AWS Resources

- **Amazon ECS Fargate** – two services (`web`, `api`) deployed via Docker images in ECR.
- **Application Load Balancer** – path-based routing (`/api/*` → API task, all other paths → web task).
- **Amazon RDS PostgreSQL** – shared multi-tenant database for users, tenants, settings, alerts, etc.
- **Amazon S3 + AWS Cost and Usage Report (CUR)** – each tenant supplies their own bucket/prefix containing parquet data.
- **AWS Glue Data Catalog / Amazon Athena** – query interface used by the FastAPI service to read tenant CUR data.
- **AWS Cost Explorer API** – optional extra analytics when enabled on the tenant account.
- **AWS IAM (AssumeRole)** – cross-account role created by tenants through `cfn/connect-aws-billing.yml` with a required ExternalId.

Repository highlights:
- `web-app/` – React SPA (Vite + React Query + Context API).
- `api/` – FastAPI backend with SQLModel, Pydantic, boto3 integrations.
- `cfn/connect-aws-billing.yml` – CloudFormation template tenants run in their account to provision the read-only role.
- `build_and_deploy.sh` – helper script to build Docker images, push to ECR, and roll the ECS services.

