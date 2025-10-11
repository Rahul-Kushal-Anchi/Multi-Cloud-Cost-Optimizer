import os, io, csv, json
from datetime import datetime, timezone
from decimal import Decimal

import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

DATA_LAKE_BUCKET = os.environ["DATA_LAKE_BUCKET"]
DDB_TABLE_NAME = os.environ["DDB_TABLE"]
table = dynamodb.Table(DDB_TABLE_NAME)

def _sum_unblended_cost_csv(body_bytes: bytes) -> float:
    f = io.StringIO(body_bytes.decode("utf-8"))
    reader = csv.DictReader(f)
    total = 0.0
    for row in reader:
        val = row.get("UnblendedCost") or row.get("unblended_cost") or row.get("Cost") or "0"
        try:
            total += float(val)
        except Exception:
            pass
    return total

def lambda_handler(event, context):
    # Support S3 event formats (S3 -> EventBridge -> SQS -> Lambda)
    records = []
    if "Records" in event:
        records = event["Records"]
    elif "detail" in event:
        d = event["detail"]
        b = d.get("bucket", {}).get("name")
        k = d.get("object", {}).get("key")
        if b and k:
            records = [{"s3": {"bucket": {"name": b}, "object": {"key": k}}}]

    processed = []
    now = datetime.now(timezone.utc)
    y, m, d = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    ds = now.strftime("%Y-%m-%d")

    for r in records:
        bucket = r["s3"]["bucket"]["name"]
        key = r["s3"]["object"]["key"]

        # read raw object
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()

        # sum costs (csv only for this first validation step)
        total = _sum_unblended_cost_csv(body)

        # write curated copy (csv) to cost lake for now
        curated_key = f"curated/provider=aws/year={y}/month={m}/day={d}/{os.path.basename(key)}"
        s3.put_object(Bucket=DATA_LAKE_BUCKET, Key=curated_key, Body=body)

        # upsert daily total in DynamoDB
        table.put_item(Item={
            "pk": f"aws#{ds}",
            "provider": "aws",
            "date": ds,
            "total_cost_usd": Decimal(str(round(total, 6))),
            "ingested_key": key,
            "updated_at": now.isoformat(),
        })

        processed.append({"bucket": bucket, "key": key, "total_cost_usd": total, "curated_key": curated_key})

    return {"statusCode": 200, "body": json.dumps({"processed": processed})}
