# Call Center Analytics Pipeline

This project provides a serverless analytics pipeline for call center data. It leverages various AWS services such as S3, SQS, SNS, CloudWatch, DynamoDB, and Lambda. The pipeline is defined and deployed using the AWS Serverless Application Model (SAM).

## Architecture

The pipeline consists of the following components:

- **S3 Buckets**: Used for storing incoming data (CallCenterBucket) and failure events (FailureEventsBucket).
- **DynamoDB Table**: Stores aggregated metrics (CallCenterMetricsTable).
- **SQS Queues**: Used for managing validated data (ValidatedDataQueue and ValidatedDataDLQ) and error data (ErrorQueue and ErrorDataDLQ).
- **SNS Topics**: Used for alerting on data validation failures (ValidationFailureTopic) and data processing failures (ProcessingFailureTopic).
- **Lambda Functions**: Used for validating incoming data (DataValidatorFunction) and processing validated data (DataProcessorFunction).

## Deployment

The pipeline is defined in the `template.yaml` file and can be deployed using AWS SAM. Before deploying, make sure to set the `ProjectName` and `Environment` parameters in the `template.yaml` file.

To deploy the pipeline, run the following command:

