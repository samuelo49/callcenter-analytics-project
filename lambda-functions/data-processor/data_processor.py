import boto3
import os
import json
from botocore.exceptions import BotoCoreError, ClientError
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
dynamodb_client = boto3.resource('dynamodb')

# Get environment variables
failure_topic_arn = os.environ['PROCESSING_FAILURE_TOPIC_ARN']
failure_bucket = os.environ['FAILURE_BUCKET']
table_name = os.environ['PROCESSED_TABLE_NAME']
table = dynamodb_client.Table(table_name)

def parse_sqs_message(record):
    """
    Parse the SQS message and extract the agent ID, start time, and duration.

    Args:
        record (dict): The SQS message record.

    Returns:
        tuple: A tuple containing the agent ID, start time, and duration.

    Raises:
        KeyError: If the required keys are not in the SQS message.
        ValueError: If the start time cannot be parsed.
    """
    try:
        ctr_data = json.loads(record['body'])
        agent_id = ctr_data['agent']['agentId']
        start_time = datetime.strptime(ctr_data['startTime'], '%Y-%m-%dT%H:%M:%SZ').date()
        duration_seconds = ctr_data.get('durationSeconds', 0)
        return agent_id, start_time, duration_seconds
    except KeyError as e:
        logging.error(f"Required key not found in SQS message: {e}")
        raise

def write_to_dynamodb(agent_id, start_time, duration_seconds):
    """
    Write the data to DynamoDB.

    Args:
        agent_id (str): The agent ID.
        start_time (datetime.date): The start time of the call.
        duration_seconds (int): The duration of the call in seconds.

    Returns:
        None

    """
    try:
        table.put_item(
            Item={
                'agentId': agent_id,
                'callDate': str(start_time),
                'totalCallDuration': duration_seconds
            }
        )
    except (BotoCoreError, ClientError) as e:
        logging.error(f"Failed to write data to DynamoDB: {e}")
        raise

def store_failed_event(record):
    """
    Store the failed event in S3.

    Args:
        record (dict): The failed event record.

    Returns:
        None

    """
    try:
        error_key = f"errors/failed_event_{datetime.now(datetime.timezone.utc).isoformat()}.json"
        s3_client.put_object(
            Bucket=failure_bucket,
            Key=error_key,
            Body=json.dumps(record)
        )
    except (BotoCoreError, ClientError) as e:
        logging.error(f"Failed to store event in S3: {e}")
        raise

def send_failure_notification(error_message):
    """
    Send a failure notification via SNS.

    Args:
        error_message (str): The error message.

    Returns:
        None

    """
    try:
        sns_client.publish(
            TopicArn=failure_topic_arn,
            Message=error_message,
            Subject="Processing Failure Alert"
        )
    except (BotoCoreError, ClientError) as e:
        logging.error(f"Failed to send failure notification: {e}")
        raise

def handler(event, context):
    """
    Process the event records and write the data to DynamoDB.

    Args:
        event (dict): The event data containing the records to process.
        context (object): The context object provided by AWS Lambda.

    Returns:
        None

    Raises:
        Exception: If there is an error processing the event.

    """
    for record in event['Records']:
        try:
            agent_id, start_time, duration_seconds = parse_sqs_message(record)
            write_to_dynamodb(agent_id, start_time, duration_seconds)
            logger.info(f"Successfully processed event for agent {agent_id}.")
        except Exception as e:
            error_message = f"Error processing event: {record}. Reason: {str(e)}"
            logger.error(error_message)
            store_failed_event(record)
            send_failure_notification(error_message)
