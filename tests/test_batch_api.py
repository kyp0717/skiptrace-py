import unittest
from src.batch_api_connector import BatchAPI


class TestBatchAPI(unittest.TestCase):
    def test_send_skip_trace_request(self):
        """
        Tests that the send_skip_trace_request method can connect to the sandbox API and get a response.
        """
        api_token = "test_token"
        connector = BatchAPI(api_token)
        address = "123 Main St, Anytown, USA"
        response = connector.send_skip_trace_request(address)
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()
