# AWS Cost Optimizer

**A SaaS portal for onboarding AWS customers and delivering real-time cost intelligence backed by AWS CUR, Athena, and Cost Explorer.**

> 💡 **Built with AI-Assisted Development:** All major features were planned with ChatGPT and implemented in Cursor.
>
> ☁️ **AWS-Only:** The platform focuses on AWS financial operations (FinOps) today. Multi-cloud support is out of scope.

---

## 🚀 What This Platform Delivers

| Persona               | Highlights                                                                                 |
|-----------------------|--------------------------------------------------------------------------------------------|
| **Global Owner**      | Manage tenants, promote admins, connect CUR sources, monitor health across customers.      |
| **Tenant Admin/User** | Self-service onboarding, connect AWS account via CloudFormation, explore live cost data.   |
| **FinOps Analysts**   | Drill into dashboards, alerts, optimization recommendations, and savings opportunities.     |

### Key Capabilities

- 🔐 **Multi-tenant authentication** with role-based access (`global_owner`, `owner`, `admin`, `member`).
- 🔄 **Onboarding workflow**: public signup, tenant activation, AWS connection with ExternalId.
- 📊 **React dashboard** pulling live metrics from CUR via Athena and Cost Explorer.
- 🧠 **Optimization insights**: dynamic alerts, savings opportunities, quick stats across the app.
- ⚙️ **Persistent settings**: profile, notifications, alerts, security preferences, password changes.
- ☁️ **Production deployment** on AWS ECS Fargate (API + SPA), fronted by an ALB, packaged via Docker & ECR.

### Tech Stack Snapshot

- **Frontend**: React, React Router, React Query, Context API.
- **Backend**: FastAPI, SQLModel, PostgreSQL, Pydantic, boto3.
- **AWS Data Plane**: CUR in S3, Athena (CTAS queries), Cost Explorer, IAM AssumeRole with ExternalId.
- **Runtime & Deployment**: Docker, AWS ECS Fargate, AWS ECR, build-and-deploy automation script.

---

## 🧭 Repository Structure (high level)

```
multi-cloud-cost-optimizer/
├── api/                        # FastAPI application
│   ├── main.py                 # Entrypoint with REST endpoints
│   ├── auth_onboarding/        # Auth, onboarding, admin routes
│   ├── secure/aws/             # AWS integrations (Athena, STS assume role)
│   └── tests/                  # API tests
├── web-app/                    # React single-page application
│   ├── src/
│   │   ├── pages/              # Dashboard, Analytics, Optimizations, Alerts, Admin, Settings
│   │   ├── components/         # Navbar, Sidebar, shared widgets
│   │   └── contexts/           # Auth & metrics providers
│   └── package.json
├── cfn/connect-aws-billing.yml # Tenant-facing CloudFormation template for cross-account role
├── build_and_deploy.sh         # Helper script to build & push Docker images + update ECS
└── docs/                       # Additional documentation (CODE_REFERENCE.md, etc.)
```

> Legacy Streamlit/ETL references were removed; the project is now a React + FastAPI SaaS portal.

---

## 🛠️ Getting Started (Local Development)

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+ (local or remote)
- AWS account with CUR + Athena access for live data (optional for local dev)

### 1. Clone & bootstrap

```bash
git clone https://github.com/Rahul-Kushal-Anchi/Multi-Cloud-Cost-Optimizer.git
cd multi-cloud-cost-optimizer
```

### 2. Backend setup (FastAPI)

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment variables (sample)
export DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/cost_optimizer"
export JWT_SECRET="change-me"
export ALLOW_PUBLIC_SIGNUP="true"

# Run the API locally
uvicorn api.main:app --host 0.0.0.0 --port 9000 --reload
```

API docs available at `http://localhost:9000/api/docs`.

### 3. Frontend setup (React)

```bash
cd web-app
npm install

# Point the SPA at the backend
export REACT_APP_API_URL="http://localhost:9000/api"

npm run dev   # Vite dev server (default port 5173)
```

Visit `http://localhost:5173` – the login page supports both sign-in and new-account setup.

---

## 🔄 Tenant Onboarding & AWS Connection

1. **Global owner login**: promote a user via the admin script or direct DB update (`role=global_owner`).
2. **Create tenant**: global owner uses the Admin panel or `/api/admin/tenants` endpoints.
3. **Public signup (optional)**: enable via `ALLOW_PUBLIC_SIGNUP=true`, new tenants land with `trialing` status.
4. **Connect AWS account**:
   - Launch the CloudFormation stack `cfn/connect-aws-billing.yml` in the tenant’s AWS account.
   - Capture `VendorRoleArn` and `ExternalId` from the stack outputs.
   - In the portal, go to **Connect AWS** and supply:
     - `AWS Role ARN`
     - `External ID`
     - CUR bucket & prefix
     - Athena database, table, workgroup, results bucket/prefix
5. **Verify data flow**:
   - After the first CUR parquet delivery, dashboards populate automatically.
   - The sidebar quick stats, main dashboard cards, analytics charts, optimizations, and alerts all read from live CUR.

> The backend guards against missing CUR data: if only manifest/DDL files exist, responses fall back to zeros instead of throwing errors.

---

## ☁️ Production Deployment (AWS ECS)

The repo ships with `build_and_deploy.sh`, which:

1. Logs in to ECR.
2. Builds and tags the **web** and **api** Docker images.
3. Pushes to `899156640791.dkr.ecr.us-east-1.amazonaws.com`.
4. Updates the ECS services (`aws-cost-optimizer-dev-web` and `aws-cost-optimizer-dev-api`) with `--force-new-deployment`.

```bash
./build_and_deploy.sh
```

### Runtime expectations

- **Web** container serves the React SPA via `serve`.
- **API** container runs `uvicorn api.main:app` on port 8000.
- ECS task definitions should include:
  - `DATABASE_URL`, `JWT_SECRET`, `ALLOW_PUBLIC_SIGNUP`
  - `AWS_REGION`, and any Cost Explorer/Athena specific overrides if necessary.
- Health checks hit `/healthz` on the API container and `/` on the web container.

---

## 🧪 Testing & Tooling

- **API tests**: `pytest api/tests` (includes auth & health checks).
- **Frontend linting**: `npm run lint` inside `web-app`.
- **Formatting**: Prettier for React, black/isort for FastAPI.
- **Docs**: `docs/CODE_REFERENCE.md` summarises endpoints, contexts, and hooks.

---

## 📚 Additional Documentation

- [docs/CODE_REFERENCE.md](docs/CODE_REFERENCE.md) – living reference for API + frontend modules.
- [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) – operational notes for ECS/ALB setup.
- [cfn/connect-aws-billing.yml](cfn/connect-aws-billing.yml) – tenant CloudFormation template.

Legacy docs (e.g., `PROJECT_STATUS.md`, `EVENT_DRIVEN_ROADMAP.md`) describe the original Streamlit/Lambda architecture and are kept for historical context only.

---

## 📈 Live Environments

- **Portal**: `http://aws-cost-optimizer-dev-alb-2097253605.us-east-1.elb.amazonaws.com/login`
- **API health**: `http://aws-cost-optimizer-dev-alb-2097253605.us-east-1.elb.amazonaws.com/api/healthz`

*(Internal use – ALB is currently public for evaluation. Lock down via WAF or authentication gateway before production launch.)*

---

## 🙌 Credits & License

- © Rahul Kushal Anchi – released under the [MIT License](LICENSE).

Enjoy simplifying your AWS cost visibility! 💸🚀
