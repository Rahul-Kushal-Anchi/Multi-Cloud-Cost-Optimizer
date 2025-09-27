# Multi-Cloud Cost Optimizer

Capstone project scaffold. Start in **AWS** using Cursor, then extend to **GCP/Azure**.

## Quick Start

```bash
# 1) Create virtual env
python3 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt

# 2) Validate tools
aws --version
terraform -version

# 3) Configure AWS credentials
aws configure sso  # or 'aws configure' with keys
aws sts get-caller-identity

# 4) Terraform (AWS)
cd infra/aws
terraform init
terraform plan
terraform apply
```

See **docs/Architecture.md** for the end-to-end architecture.
