# End-to-End Architecture (Summary)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                               Cloud Platform Events                           │
│ AWS: S3 CUR, CloudTrail/CloudWatch, EKS/ASG                                   │
│ Azure: Cost Mgmt Export→BlobCreated, Activity Logs / Metrics                  │
│ GCP: BigQuery Billing Export appends, Cloud Audit Logs / Monitoring           │
└───────────────┬───────────────────────────┬───────────────────────────┬───────┘
                │                           │                           │
        ┌───────▼────────┐           ┌──────▼─────────┐          ┌──────▼───────┐
        │ AWS EventBridge│           │ Azure EventGrid│          │  GCP Pub/Sub │
        │ (+ Kinesis opt)│           │ + Service Bus  │          │  (native bus)│
        └────────┬───────┘           └────────┬───────┘          └──────┬───────┘
                 │                             │                           │
                 └─────────────── fan-in via provider adapters ────────────┘
                                      (unified event schema)
                                         │
                               ┌─────────▼─────────┐
                               │ Serverless ETL    │
                               │  Lambda / Az Fn   │
                               │  / Cloud Fn       │
                               │  • validate auth  │
                               │  • map → FOCUS    │
                               │  • write RAW      │
                               │  • emit cost_ing. │
                               └─────────┬─────────┘
                                         │
                   ┌─────────────────────▼─────────────────────┐
                   │            Storage & ELT (Hybrid)         │
                   │  RAW  : S3 / ADLS / GCS  (by dt/provider) │
                   │  CURATED: Parquet tables (Data Lakehouse) │
                   │           + Warehouse views                │
                   │  Engines: Athena / Synapse / BigQuery     │
                   │  ELT: MERGE/UPSERT (idempotent loads)     │
                   └───────────────┬───────────────────────────┘
                                   │
            ┌──────────────────────▼────────────────────────┐
            │           Intelligence Layer (AI/Rules)       │
            │  • Real-time anomaly: rolling z / EWMA / IF   │
            │  • Forecasts: Prophet/XGBoost                 │
            │  • Optimizer: rightsizing, commitments        │
            │    (RI/SP, Azure Reservations, GCP CUDs),     │
            │    storage tiering, orphan cleanup            │
            │  • Cross-cloud SKU price/perf comparer        │
            │  • Savings tracker & ROI scoring              │
            └──────────────────────┬────────────────────────┘
                                   │
     ┌─────────────────────────────▼─────────────────────────────┐
     │            Serving, Dashboards & Notifications            │
     │  API: FastAPI (REST/GraphQL), auth (Cognito/Entra/GAI)   │
     │  UI : Grafana/QuickSight/Power BI/Looker/Streamlit       │
     │  Notifs: SNS/Email/Slack/Teams/Jira + runbooks           │
     │  (optional) approvals → auto-remediation playbooks       │
     └─────────────────────────────┬─────────────────────────────┘
                                   │
                      ┌────────────▼────────────┐
                      │   Governance & Guardrails│
                      │ Budgets, tag/label policy│
                      │ SCP/Policy/Org Policies  │
                      │ FinOps KPIs & chargeback │
                      └───────────────────────────┘
```
