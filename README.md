# AWS Cost Optimizer

**A production-grade, event-driven platform for optimizing AWS costs with advanced analytics and automation**

> 💡 **Built with AI-Assisted Development:** This project demonstrates modern development practices using ChatGPT for design and Cursor for implementation.

> 🎯 **AWS-Focused:** This project is exclusively focused on AWS cost optimization. We are not implementing multi-cloud support (GCP, Azure).

---

## 🎯 Overview

AWS Cost Optimizer is a comprehensive platform that:
- **Ingests** AWS Cost and Usage Reports (CUR) automatically
- **Processes** billing data through an event-driven ETL pipeline
- **Analyzes** spending patterns and identifies cost anomalies
- **Recommends** cost optimization opportunities (rightsizing, waste removal, commitments)
- **Alerts** on anomalies and budget overruns via SNS
- **Stores** data in a scalable data lake for historical analysis

**Tech Stack:** Python, Terraform, AWS Lambda, EventBridge, SQS, DynamoDB, S3, SNS, FastAPI

---

## 📚 Learning Resources

**New to this project? Start here:**

### 1. **[Learning Guide](docs/Learning_Guide.md)** 📖
Comprehensive guide covering all concepts and technologies:
- Cloud fundamentals (AWS, GCP, Azure)
- Infrastructure as Code (Terraform)
- Serverless computing (Lambda, Cloud Functions)
- Data engineering (ETL, data lakes, Parquet)
- API development (FastAPI)
- Cost optimization algorithms
- AI-assisted development workflows

**Start here if:** You want to understand the technologies and concepts

### 2. **[AI Tools Mastery](docs/AI_Tools_Mastery.md)** 🤖
Master ChatGPT and Cursor for 10x development speed:
- ChatGPT prompting techniques
- Cursor commands and workflows
- The perfect AI-assisted development workflow
- Real-world examples
- Common pitfalls and how to avoid them

**Start here if:** You want to maximize productivity with AI tools

### 3. **[12-Week Roadmap](docs/12_Week_Roadmap.md)** 🗓️
Day-by-day guide from zero to production:
- Week 1: AWS foundation
- Week 2: Data lake & analytics
- Week 3: FastAPI backend
- Week 4: Optimization engines
- Week 5-6: GCP integration
- Week 7-8: Azure integration
- Week 9: Dashboards
- Week 10: Real-time processing
- Week 11: Testing & CI/CD
- Week 12: Polish & demo prep

**Start here if:** You want a structured learning path

### 4. **[Quick Reference](docs/Quick_Reference.md)** ⚡
Instant answers while coding:
- ChatGPT prompt templates
- Cursor command cheatsheet
- Common code patterns
- AWS CLI commands
- Terraform commands
- Troubleshooting guide

**Start here if:** You need quick answers while working

### 5. **[Architecture](docs/Architecture.md)** 🏗️
System design and data flow:
- High-level architecture
- Component descriptions
- Data flow diagrams
- AWS/GCP/Azure specific details

**Start here if:** You want to understand the system design

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required tools
- Python 3.12+
- Terraform 1.5+
- AWS CLI 2.0+
- Git
- Docker (optional, for local testing)
- Cursor (code editor)
```

### Setup

```bash
# 1) Clone repository
git clone <your-repo-url>
cd multi-cloud-cost-optimizer

# 2) Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3) Install Python dependencies
pip install -r api/requirements.txt

# 4) Configure AWS credentials
aws configure
# Or use SSO: aws configure sso
aws sts get-caller-identity

# 5) Deploy infrastructure
cd infra/aws
terraform init
terraform plan
terraform apply
```

### Test the Pipeline

```bash
# Upload sample CUR file
aws s3 cp samples/aws_cur_sample.csv s3://cur-raw-dev-<account-id>/cur/test.csv

# Check Lambda logs
aws logs tail /aws/lambda/etl-aws-cur-parser-dev --follow

# Verify data in DynamoDB
aws dynamodb scan --table-name cost-daily-dev

# Query with Athena (in AWS Console)
SELECT * FROM cost_optimizer_db.aws_cur_curated LIMIT 10;
```

### Run the API

```bash
# Start FastAPI server
cd api
uvicorn main:app --reload

# Visit API documentation
open http://localhost:8000/docs

# Test endpoints
curl http://localhost:8000/api/v1/cost/summary?date=2025-01-15
```

---

## 📁 Project Structure

```
multi-cloud-cost-optimizer/
│
├── docs/                           # Documentation
│   └── Architecture.md            # System architecture
│
├── infra/                          # Infrastructure as Code
│   └── aws/
│       ├── main.tf                # Main Terraform configuration
│       ├── variables.tf           # Variables
│       ├── outputs.tf             # Outputs
│       └── etl_aws_cur_parser.zip # Lambda deployment package
│
├── etl/                            # ETL pipelines
│   └── aws_lambda/
│       ├── etl_aws_cur_parser/    # CUR file processor
│       │   ├── lambda_function.py # Main ETL handler
│       │   └── requirements.txt   # Lambda dependencies
│       └── signal_router/         # Real-time anomaly router
│           ├── lambda_function.py
│           └── requirements.txt
│
├── engine/                         # Optimization engines
│   ├── base.py                    # Base classes
│   ├── rightsizing.py             # Rightsizing recommendations
│   ├── commitments.py             # RI/Savings Plans analyzer
│   ├── waste.py                   # Waste detection
│   └── anomaly.py                 # Anomaly detection
│
├── api/                            # FastAPI backend
│   ├── main.py                    # FastAPI app
│   ├── routers/                   # API endpoints
│   │   ├── cost.py               # Cost endpoints
│   │   ├── recommendations.py    # Recommendations endpoints
│   │   └── alerts.py             # Alert endpoints
│   ├── models/                    # Pydantic models
│   ├── services/                  # Business logic
│   └── requirements.txt           # Python dependencies
│
├── tests/                          # Tests
│   ├── test_api.py                # API tests
│   ├── test_etl.py                # ETL tests
│   └── test_engine.py             # Engine tests
│
├── samples/                        # Sample data
│   └── aws_cur_sample.csv         # Sample AWS CUR
│
├── dashboards/                     # Visualization configs
│   ├── grafana.json               # Grafana dashboard
│   └── quicksight_template.json   # QuickSight template
│
├── Makefile                        # Common commands
└── README.md                       # This file
```

---

## 🎓 Learning Path

**Recommended approach:**

### Phase 1: Foundations (Weeks 1-3)
1. Read [Learning Guide](docs/Learning_Guide.md) - Core Concepts section
2. Follow [12-Week Roadmap](docs/12_Week_Roadmap.md) Week 1-3
3. Build AWS pipeline: S3 → Lambda → DynamoDB → Athena
4. Use [AI Tools Mastery](docs/AI_Tools_Mastery.md) for implementation
5. Reference [Quick Reference](docs/Quick_Reference.md) when stuck

### Phase 2: Backend & Analytics (Weeks 4-5)
1. Read [Learning Guide](docs/Learning_Guide.md) - FastAPI section
2. Follow [12-Week Roadmap](docs/12_Week_Roadmap.md) Week 3-4
3. Build FastAPI backend
4. Implement optimization engines
5. Create Grafana dashboards

### Phase 3: Advanced AWS Features (Weeks 6-9)
1. Implement cost anomaly detection with ML
2. Add resource optimization recommendations
3. Build cost forecasting models
4. Add AWS Organizations support
5. Implement multi-account cost aggregation

### Phase 4: Production (Weeks 10-12)
1. Follow [12-Week Roadmap](docs/12_Week_Roadmap.md) Week 10-12
2. Add comprehensive testing
3. Set up CI/CD
4. Harden security
5. Polish for demos

---

## 🤖 AI-Assisted Development

This project is designed to be built with AI assistance:

### Using ChatGPT
- **Understanding:** "Explain AWS Lambda cold starts"
- **Design:** "Design a cost anomaly detection system"
- **Review:** "Review this code for production readiness"
- **Debug:** "Why am I getting this error?"

### Using Cursor
- **Generate:** Cmd+I → "Create Lambda function for X"
- **Edit:** Cmd+K → "Add error handling"
- **Explore:** Cmd+L → "Where is DynamoDB table created?"

**See [AI Tools Mastery](docs/AI_Tools_Mastery.md) for comprehensive guide**

---

## 🏗️ Architecture

**Event-Driven Architecture Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│                   AWS Cost Data Source                       │
│              (Cost and Usage Reports - CUR)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                ┌─────────────────────┐
                │   S3 Cost Lake      │
                │  (Raw CUR Files)    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   EventBridge Bus   │
                │  (Event Router)     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   SQS Queue         │
                │  + Dead Letter Q    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Lambda Function   │
                │  ETL CUR Parser     │
                └──────────┬──────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
┌──────────────────┐          ┌────────────────────┐
│  DynamoDB Table  │          │  S3 Data Lake      │
│  (Daily Totals)  │          │  (Curated Data)    │
└──────────────────┘          └────────────────────┘
           │
           ▼
┌──────────────────┐
│ Optimization     │
│ Engines          │
│ • Rightsizing    │
│ • Waste          │
│ • Anomaly        │
│ • Commitments    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   FastAPI        │
│   Backend        │
└─────────┬────────┘
          │
    ┏─────┻─────┓
    ▼           ▼
┌─────────┐  ┌────────┐
│ Grafana │  │  SNS   │
│Dashboard│  │ Alerts │
└─────────┘  └────────┘
```

**See [Architecture.md](docs/Architecture.md) for detailed diagrams**

---

## 🔧 Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=api --cov=engine --cov-report=term-missing

# Specific test file
pytest tests/test_api.py -v

# Specific test
pytest tests/test_api.py::test_get_cost_summary -v
```

### Linting & Formatting

```bash
# Format code
black api/ engine/ etl/

# Lint
pylint api/ engine/
flake8 api/ engine/

# Type checking
mypy api/ engine/
```

### Deploying Infrastructure

```bash
# AWS
cd infra/aws
terraform plan
terraform apply

# GCP (future)
cd infra/gcp
terraform plan
terraform apply

# Azure (future)
cd infra/azure
terraform plan
terraform apply
```

### Common Commands (Makefile)

```bash
# Deploy AWS infrastructure
make deploy-aws

# Run API locally
make run-api

# Run tests
make test

# Format code
make format

# Package Lambda functions
make package-lambdas

# Deploy everything
make deploy-all
```

---

## 📊 Features

### Current (AWS Only)
- ✅ AWS CUR ingestion pipeline
- ✅ S3 → EventBridge → SQS → Lambda → DynamoDB
- ✅ Parquet data lake with Athena queries
- ✅ FastAPI backend with cost endpoints
- ✅ Rightsizing recommendations
- ✅ Waste detection (unattached EBS, unused IPs, etc.)
- ✅ Anomaly detection (Z-score based)
- ✅ CloudWatch monitoring and alerts
- ✅ Grafana dashboards

### Planned
- 🔄 Commitment recommendations (RI/Savings Plans)
- 🔄 ML-based anomaly detection
- 🔄 Budget management
- 🔄 Cost forecasting
- 🔄 Tag compliance checker
- 🔄 Resource rightsizing recommendations
- 🔄 Idle resource detection
- 🔄 AWS Organizations support
- 🔄 Multi-account cost aggregation
- 🔄 CI/CD pipeline

---

## 🎯 Use Cases

1. **FinOps Teams**
   - Monitor and optimize cloud spend
   - Generate recommendations
   - Track savings over time

2. **Engineering Teams**
   - Understand cost impact of changes
   - Get alerted on anomalies
   - Right-size resources

3. **Executives**
   - Unified view of multi-cloud costs
   - Cost trends and forecasts
   - ROI tracking

4. **Learning & Demo**
   - Capstone project
   - Portfolio piece
   - Interview showcase

---

## 🤝 Contributing

This is a personal learning project, but feedback is welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Workflow
1. Use ChatGPT for design and understanding
2. Use Cursor for implementation
3. Write tests for new features
4. Update documentation
5. Commit with descriptive messages

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

**Technologies:**
- AWS (Lambda, S3, DynamoDB, Athena)
- Terraform (Infrastructure as Code)
- FastAPI (Modern Python API framework)
- Grafana (Visualization)

**AI Tools:**
- ChatGPT (OpenAI) - For design and learning
- Cursor - For AI-assisted coding

**Resources:**
- AWS Documentation
- FinOps Foundation
- Terraform Registry
- FastAPI Documentation

---

## 📞 Contact

**Questions? Stuck? Want to share progress?**

- Open an issue in this repository
- Connect on LinkedIn
- Join FinOps Foundation Slack

---

## 🎓 From Zero to Hero

**Starting from scratch?**

1. **Day 1:** Read this README, then start [12-Week Roadmap](docs/12_Week_Roadmap.md) Day 1
2. **Week 1:** AWS foundation - deploy your first Lambda
3. **Week 3:** Working AWS pipeline with dashboard
4. **Week 6:** Multi-cloud support
5. **Week 12:** Production-ready demo

**By the end:** You'll have a portfolio-worthy project and deep cloud expertise!

**Ready to start?** 

👉 **Begin with [12-Week Roadmap - Day 1](docs/12_Week_Roadmap.md#day-1-environment-setup-monday)**

---

**Happy building! 🚀**
