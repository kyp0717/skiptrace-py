
import unittest
import json
from src.batch_api_connector import BatchAPIConnector

class TestBatchAPIConnector(unittest.TestCase):
    def test_send_skip_trace_request(self):
        """
        Tests that the send_skip_trace_request method can connect to the sandbox API and get a response.
        """
        connector = BatchAPIConnector(env='sandbox')
        with open('tests/batchapi_test_cases.json', 'r') as f:
            test_cases = json.load(f)

        for i, test_case in enumerate(test_cases['requests']):
            with self.subTest(i=i):
                address = test_case['propertyAddress']
                print(f"\nInput: {address}")
                response = connector.send_skip_trace_request(address)
                print(f"Output: {response}")
                self.assertIsInstance(response, list)
                if response:
                    self.assertIsInstance(response[0], str)

if __name__ == '__main__':
    unittest.main()
