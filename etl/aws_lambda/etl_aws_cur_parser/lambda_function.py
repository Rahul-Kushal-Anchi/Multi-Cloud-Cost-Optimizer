import os, io, csv, json
from datetime import datetime, timezone
from decimal import Decimal

import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

DATA_LAKE_BUCKET = os.environ["DATA_LAKE_BUCKET"]
DDB_TABLE_NAME = os.environ["DDB_TABLE"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
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

def _extract_s3_info_from_event(event):
    """Extract S3 bucket and key from various event formats"""
    # Handle SQS events (from EventBridge)
    if "Records" in event:
        for record in event["Records"]:
            if "body" in record:
                # SQS message body contains the EventBridge event
                body = json.loads(record["body"])
                if "detail" in body and "bucket" in body["detail"]:
                    return body["detail"]["bucket"]["name"], body["detail"]["object"]["key"]
            elif "s3" in record:
                # Direct S3 event format
                return record["s3"]["bucket"]["name"], record["s3"]["object"]["key"]
    
    # Handle direct EventBridge events
    elif "detail" in event:
        if "bucket" in event["detail"]:
            return event["detail"]["bucket"]["name"], event["detail"]["object"]["key"]
    
    return None, None

def _publish_sns_notification(processed_items):
    """Publish success notification to SNS"""
    try:
        message = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "processed_files": len(processed_items),
            "details": processed_items
        }
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message, indent=2),
            Subject=f"AWS Cost Optimizer: {len(processed_items)} file(s) processed successfully"
        )
        print(f"Success notification published to SNS: {SNS_TOPIC_ARN}")
    except Exception as e:
        print(f"Failed to publish SNS notification: {str(e)}")

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    processed = []
    now = datetime.now(timezone.utc)
    y, m, d = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
    ds = now.strftime("%Y-%m-%d")

    # Extract S3 bucket and key from event
    bucket, key = _extract_s3_info_from_event(event)
    
    if not bucket or not key:
        print("No valid S3 bucket/key found in event")
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid event format"})}

    try:
        print(f"Processing file: s3://{bucket}/{key}")
        
        # Read raw object from S3
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()

        # Sum costs (csv only for this first validation step)
        total = _sum_unblended_cost_csv(body)
        print(f"Total cost calculated: ${total}")

        # Write curated copy (csv) to cost lake with partitioning
        curated_key = f"curated/provider=aws/year={y}/month={m}/day={d}/{os.path.basename(key)}"
        s3.put_object(Bucket=DATA_LAKE_BUCKET, Key=curated_key, Body=body)
        print(f"Curated file written to: s3://{DATA_LAKE_BUCKET}/{curated_key}")

        # Upsert daily total in DynamoDB
        table.put_item(Item={
            "pk": f"aws#{ds}",
            "provider": "aws",
            "date": ds,
            "total_cost_usd": Decimal(str(round(total, 6))),
            "ingested_key": key,
            "updated_at": now.isoformat(),
        })
        print(f"Daily total updated in DynamoDB: ${total} for {ds}")

        processed_item = {
            "bucket": bucket,
            "key": key,
            "total_cost_usd": total,
            "curated_key": curated_key,
            "processed_at": now.isoformat()
        }
        processed.append(processed_item)

        # Publish success notification to SNS
        _publish_sns_notification(processed)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Processing completed successfully",
                "processed": processed
            })
        }

    except Exception as e:
        error_msg = f"Error processing file s3://{bucket}/{key}: {str(e)}"
        print(error_msg)
        
        # Publish error notification to SNS
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "error",
                    "error": str(e),
                    "bucket": bucket,
                    "key": key
                }, indent=2),
                Subject="AWS Cost Optimizer: Processing Error"
            )
        except Exception as sns_error:
            print(f"Failed to publish error notification: {str(sns_error)}")
        
        # Re-raise the exception so Lambda marks the message as failed
        raise e