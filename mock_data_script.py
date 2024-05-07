import os
import json
import random
import boto3
from datetime import datetime, timedelta

# AWS clients
s3 = boto3.client('s3')
# Fetch the bucket name from an environment variable
bucket_name = os.getenv('BUCKET_NAME')

if not bucket_name:
    raise Exception('The BUCKET_NAME environment variable is not set')

# Constants for generating mock data
agents = [
    {"agentId": "agent-001", "agentName": "Alice"},
    {"agentId": "agent-002", "agentName": "Bob"},
    {"agentId": "agent-003", "agentName": "Charlie"}
]

# Generate random contact trace records
def generate_ctr_data():
    start_time = datetime.utcnow() - timedelta(days=random.randint(0, 30))
    end_time = start_time + timedelta(minutes=random.randint(5, 30))
    agent = random.choice(agents)
    return {
        "contactId": f"contact-{random.randint(1000, 9999)}",
        "startTime": start_time.isoformat() + "Z",
        "endTime": end_time.isoformat() + "Z",
        "durationSeconds": int((end_time - start_time).total_seconds()),
        "agent": agent,
        "queue": {
            "queueId": "queue-123",
            "queueName": "Support Queue"
        },
        "attributes": {
            "callType": random.choice(["inbound", "outbound"]),
            "customerSatisfactionScore": random.randint(1, 5),
            "afterCallWorkSeconds": random.randint(60, 180)
        },
        "status": {
            "connectedToAgent": True,
            "queueTimeSeconds": random.randint(10, 120),
            "disconnectReason": "customer_hangup"
        }
    }

# Upload generated data to S3
def upload_mock_data(num_files=10):
    for i in range(num_files):
        ctr_data = generate_ctr_data()
        object_key = f"incoming/contact_{i+1}.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(ctr_data)
        )
        print(f"Uploaded: {object_key}")

if __name__ == "__main__":
    # Adjust the number of files to generate and upload as needed
    upload_mock_data(5)
