# 🚀 Event-Driven Architecture Implementation Roadmap

## 📋 Architecture Overview

**Target Architecture:**
```
S3 (CUR Upload) → EventBridge → SQS → Lambda → DynamoDB → SNS
                                    ↓
                                   DLQ (Failed Events)
```

**Current vs Target:**
- **Before**: S3 → Lambda (Direct)
- **After**: S3 → EventBridge → SQS → Lambda → DynamoDB → SNS

## 🎯 Implementation Steps

### Phase 1: Deploy Event-Driven Infrastructure ✅

**Step 1: Infrastructure Deployment**
```bash
cd infra/aws
terraform plan
terraform apply -auto-approve
```

**What's Being Deployed:**
- ✅ SQS Queue (`cur-processing-queue-dev`) + DLQ (`cur-processing-dlq-dev`)
- ✅ EventBridge Custom Event Bus (`cost-optimizer-event-bus-dev`)
- ✅ EventBridge Rule for S3 CSV uploads
- ✅ EventBridge Target routing to SQS
- ✅ Lambda function with SQS trigger
- ✅ IAM roles and policies for all components
- ✅ S3 EventBridge notifications

### Phase 2: Test the Complete Pipeline

**Step 2: Upload Test File**
```bash
cd /Users/rahulkushalanchi/Downloads/multi-cloud-cost-optimizer
aws s3 cp samples/aws_cur_sample.csv s3://costlake-dev-450dc612/event_driven_test.csv
```

**Step 3: Monitor the Pipeline**
```bash
# Check SQS queue for messages
aws sqs get-queue-attributes --queue-url $(aws sqs get-queue-url --queue-name cur-processing-queue-dev --query QueueUrl --output text) --attribute-names All

# Check Lambda logs
aws logs tail /aws/lambda/etl-aws-cur-parser-dev --since 2m

# Check DynamoDB for new entries
aws dynamodb scan --table-name cost_daily_dev

# Check SNS notifications (if subscribed)
aws sns list-subscriptions-by-topic --topic-arn $(aws sns list-topics --query 'Topics[?contains(TopicArn, `cost-alerts-dev`)].TopicArn' --output text)
```

### Phase 3: Enhanced Features

**Step 4: Add Cost Anomaly Detection**
- Monitor cost spikes
- Alert on unusual spending patterns
- Implement ML-based anomaly detection

**Step 5: Resource Optimization Scanner**
- Find unused EC2 instances
- Identify orphaned EBS volumes
- Detect idle RDS instances

**Step 6: Cost Forecasting**
- Predict future costs based on trends
- Budget recommendations
- Seasonal pattern analysis

## 🔧 Key Components

### 1. EventBridge Custom Event Bus
- **Name**: `cost-optimizer-event-bus-dev`
- **Purpose**: Central hub for all cost-related events
- **Benefits**: Decoupled, scalable, extensible

### 2. SQS Queue with DLQ
- **Main Queue**: `cur-processing-queue-dev`
- **DLQ**: `cur-processing-dlq-dev`
- **Benefits**: Reliable processing, error handling, retry mechanism

### 3. Enhanced Lambda Function
- **Features**:
  - SQS event processing
  - SNS notifications
  - Error handling and reporting
  - Detailed logging

### 4. SNS Notifications
- **Topic**: `cost-alerts-dev`
- **Types**: Success, Error, Anomaly alerts
- **Extensible**: Can add email, SMS, webhook subscriptions

## 📊 Monitoring & Observability

### CloudWatch Metrics to Monitor:
- SQS queue depth
- Lambda execution duration
- DynamoDB read/write capacity
- EventBridge rule invocations
- SNS message delivery

### Log Groups:
- `/aws/lambda/etl-aws-cur-parser-dev`
- EventBridge events in CloudWatch Logs

## 🚨 Error Handling

### DLQ Processing:
1. Failed messages go to DLQ after 3 retries
2. Messages retained for 14 days
3. Manual reprocessing capability
4. Root cause analysis

### SNS Error Notifications:
- Processing failures
- S3 access errors
- DynamoDB write errors
- Configuration issues

## 🔄 Future Enhancements

### 1. Multi-Account Support
- Cross-account EventBridge rules
- Centralized cost aggregation
- Account-specific alerts

### 2. Advanced Analytics
- Cost trend analysis
- Resource utilization patterns
- Optimization recommendations

### 3. Automation
- Auto-stop non-production resources
- Scheduled cleanup tasks
- Cost-based auto-scaling

## 📝 Testing Checklist

- [ ] Upload CSV file triggers EventBridge
- [ ] EventBridge rule routes to SQS
- [ ] Lambda processes SQS message
- [ ] Data written to DynamoDB
- [ ] Curated file created in S3
- [ ] SNS notification sent
- [ ] Failed messages go to DLQ
- [ ] Error notifications work

## 🎯 Success Criteria

1. **Reliability**: 99.9% message processing success rate
2. **Performance**: <30 seconds end-to-end processing
3. **Observability**: Complete audit trail of all events
4. **Scalability**: Handle 1000+ files per hour
5. **Error Handling**: Zero data loss with proper DLQ processing
