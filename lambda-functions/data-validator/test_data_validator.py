from unittest.mock import patch
import unittest
from unittest.mock import patch
from data_validator import handler

class TestHandler(unittest.TestCase):
    """
    A test case for the handler function in the data validator module.
    """

    @patch('data_validator.s3')
    @patch('data_validator.sqs')
    def test_handler_valid_data(self, mock_sqs, mock_s3):
        """
        Test the handler function with valid data.

        This test case simulates the scenario where the data retrieved from S3 is valid.
        It verifies that the handler function sends the message to the validated queue.

        Args:
            mock_sqs: The mocked SQS client.
            mock_s3: The mocked S3 client.
        """
        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {'name': 'test-bucket'},
                        'object': {'key': 'test-object'}
                    }
                }
            ]
        }
        mock_s3.get_object.return_value = {
            'Body': {
                'read': lambda: b'{"contactId": "123", "startTime": "2022-01-01", "agent": "John Doe"}'
            }
        }
        handler(event, None)
        mock_sqs.send_message.assert_called_with(
            QueueUrl='VALIDATED_QUEUE_URL',
            MessageBody='{"contactId": "123", "startTime": "2022-01-01", "agent": "John Doe"}'
        )

    @patch('data_validator.s3')
    @patch('data_validator.sqs')
    def test_handler_invalid_data(self, mock_sqs, mock_s3):
        """
        Test the handler function with invalid data.

        This test case simulates the scenario where the data retrieved from S3 is invalid.
        It verifies that the handler function sends the message to the error queue.

        Args:
            mock_sqs: The mocked SQS client.
            mock_s3: The mocked S3 client.
        """
        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {'name': 'test-bucket'},
                        'object': {'key': 'test-object'}
                    }
                }
            ]
        }
        mock_s3.get_object.return_value = {
            'Body': {
                'read': lambda: b'{"contactId": "123", "startTime": "2022-01-01"}'
            }
        }
        handler(event, None)
        mock_sqs.send_message.assert_called_with(
            QueueUrl='ERROR_QUEUE_URL',
            MessageBody='{"contactId": "123", "startTime": "2022-01-01"}'
        )

if __name__ == '__main__':
    unittest.main()