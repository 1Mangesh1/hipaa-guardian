# AWS Lambda Reference

## Function Management

```bash
# Create function
aws lambda create-function \
  --function-name my-func \
  --runtime nodejs20.x \
  --handler index.handler \
  --role arn:aws:iam::123456789:role/lambda-role \
  --zip-file fileb://function.zip

# Create from container
aws lambda create-function \
  --function-name my-func \
  --package-type Image \
  --code ImageUri=123456789.dkr.ecr.us-east-1.amazonaws.com/my-func:latest \
  --role arn:aws:iam::123456789:role/lambda-role

# Update code
zip -r function.zip .
aws lambda update-function-code \
  --function-name my-func \
  --zip-file fileb://function.zip

# Update configuration
aws lambda update-function-configuration \
  --function-name my-func \
  --timeout 30 \
  --memory-size 512 \
  --environment "Variables={DB_HOST=mydb.cluster.amazonaws.com}"

# Delete
aws lambda delete-function --function-name my-func
```

## Invocation

```bash
# Synchronous invoke
aws lambda invoke \
  --function-name my-func \
  --payload '{"key": "value"}' \
  response.json

# Async invoke
aws lambda invoke \
  --function-name my-func \
  --invocation-type Event \
  --payload '{"key": "value"}' \
  response.json

# Dry run (validates)
aws lambda invoke \
  --function-name my-func \
  --invocation-type DryRun \
  --payload '{}' \
  response.json
```

## Aliases & Versions

```bash
# Publish version
aws lambda publish-version --function-name my-func

# Create alias
aws lambda create-alias \
  --function-name my-func \
  --name prod \
  --function-version 5

# Update alias (blue/green with traffic shifting)
aws lambda update-alias \
  --function-name my-func \
  --name prod \
  --function-version 6 \
  --routing-config AdditionalVersionWeights={"5"=0.1}
```

## Event Source Mappings

```bash
# SQS trigger
aws lambda create-event-source-mapping \
  --function-name my-func \
  --event-source-arn arn:aws:sqs:us-east-1:123:my-queue \
  --batch-size 10

# DynamoDB stream trigger
aws lambda create-event-source-mapping \
  --function-name my-func \
  --event-source-arn arn:aws:dynamodb:us-east-1:123:table/my-table/stream/xxx \
  --starting-position LATEST \
  --batch-size 100

# List mappings
aws lambda list-event-source-mappings --function-name my-func
```

## Layers

```bash
# Create layer
aws lambda publish-layer-version \
  --layer-name my-layer \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.12

# Add layer to function
aws lambda update-function-configuration \
  --function-name my-func \
  --layers arn:aws:lambda:us-east-1:123:layer:my-layer:1
```

## Logs

```bash
# View recent logs
aws logs tail /aws/lambda/my-func --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-func \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)
```

## Function URLs

```bash
# Create URL (public)
aws lambda create-function-url-config \
  --function-name my-func \
  --auth-type NONE

# Create URL (IAM auth)
aws lambda create-function-url-config \
  --function-name my-func \
  --auth-type AWS_IAM

# Get URL
aws lambda get-function-url-config --function-name my-func
```
