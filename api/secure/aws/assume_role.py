import boto3
from botocore.config import Config

def assume_vendor_role(role_arn: str, external_id: str, region: str = "us-east-1"):
    sts = boto3.client("sts", config=Config(region_name=region))
    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="CostReadSession",
        ExternalId=external_id,
        DurationSeconds=3600,
    )
    creds = resp["Credentials"]
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )
    return session
