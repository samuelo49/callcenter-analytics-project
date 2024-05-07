import unittest
from unittest.mock import MagicMock
from datetime import datetime
from test_data_processing import handler

class TestDataProcessing(unittest.TestCase):
    def test_handler(self):
        # Mock event data
        event = {
            'Records': [
                {
                    'body': '{"agent": {"agentId": "123"}, "startTime": "2022-01-01T10:00:00Z", "durationSeconds": 3600}'
                }
            ]
        }

        # Mock DynamoDB table
        table_mock = MagicMock()

        # Patch the DynamoDB resource
        with unittest.mock.patch('test_data_processing.table', table_mock):
            # Call the handler function
            handler(event, None)

        # Assert that the item was put into the table
        table_mock.put_item.assert_called_once_with(
            Item={
                'agentId': '123',
                'callDate': str(datetime(2022, 1, 1).date()),
                'totalCallDuration': 3600
            }
        )

if __name__ == '__main__':
    unittest.main()