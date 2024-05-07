import os
import json
import logging
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import botocore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
validated_queue_url = os.environ['VALIDATED_QUEUE_URL']
error_queue_url = os.environ['ERROR_QUEUE_URL']

def get_file_content(bucket_name, object_key):
    """
    Retrieves the content of a file from an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object in the S3 bucket.

    Returns:
        dict: The content of the file as a dictionary.

    Raises:
        BotoCoreError: If there is an error with AWS connectivity or configuration.
        ClientError: If there is an error with the S3 service, such as the bucket not existing.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        return json.loads(file_content)
    except botocore.exceptions.BotoCoreError as e:
        logging.error(f"Error with AWS connectivity or configuration: {e}")
        raise
    except botocore.exceptions.ClientError as e:
        logging.error(f"Error with the S3 service: {e}. Check if bucket '{bucket_name}' and object '{object_key}' exist.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"File content from bucket '{bucket_name}' and object '{object_key}' is not valid JSON: {e}")
        raise


def validate_ctr_data(ctr_data):
    """
    Validates the call center data.

    This function checks if the given call center data contains all the required fields.

    Args:
        ctr_data (dict): The call center data to be validated.

    Returns:
        bool: True if all the required fields are present in the call center data, False otherwise.
    """
    required_fields = ['contactId', 'startTime', 'agent']
    return all(field in ctr_data for field in required_fields)

def handler(event, context):
    """
    Process the event triggered by an S3 object creation and validate the CTR data.

    Args:
        event (dict): The event object containing information about the S3 object creation.
        context (object): The context object provided by AWS Lambda.

    Returns:
        None

    Raises:
        ClientError: If there is an error processing the S3 object, 
        such as if the object does not exist or if there is an issue with the S3 service.

    """
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        try:
            ctr_data = get_file_content(bucket_name, object_key)

            if validate_ctr_data(ctr_data):
                queue_url = validated_queue_url
                logger.info(f"Validated CTR data: {ctr_data}")
            else:
                queue_url = error_queue_url
                logger.warning(f"Invalid CTR data: {ctr_data}")

            sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(ctr_data))
            logger.info(f"Sent CTR data to queue: {queue_url}")

        except ClientError as e:
            logger.error(f"Error processing {object_key}: {e}")
            continue


