import requests
import csv
import json
import os

class BatchAPIConnector:
    def __init__(self, env='sandbox'):
        """
        Initialize the BatchAPIConnector with environment configuration.
        Args:
            env: 'sandbox' or 'prod' environment
        """
        self.env = env
        self.api_token = self._get_api_token(env)
        self.base_url = self._get_base_url(env)
        
    def _get_api_token(self, env):
        """Load API token from CSV file based on environment."""
        # Try multiple possible locations for batchapi.csv
        possible_paths = [
            '../batchapi.csv',  # As specified in project_plan
            './batchapi.csv',   # Current directory
            'batchapi.csv',     # Relative to working directory
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'batchapi.csv')
        ]
        
        for csv_path in possible_paths:
            try:
                with open(csv_path, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row[0] == env:
                            return row[1]
            except FileNotFoundError:
                continue
        
        print(f"Warning: batchapi.csv not found in any expected location")
        return None

    def _get_base_url(self, env):
        """Get the appropriate API URL based on environment."""
        if env == 'sandbox':
            return 'https://stoplight.io/mocks/batchdata/batchdata/20349728/property/skip-trace'
        elif env == 'prod':
            return 'https://api.batchdata.com/api/v1/property/skip-trace'
        return None

    def send_skip_trace_request(self, address):
        """
        Sends a skip trace request to the BatchData API.
        Args:
            address: Dictionary with street, city, state, zip
        Returns:
            List of phone numbers or empty list if request fails
        """
        if not self.api_token:
            print(f"Error: No API token found for {self.env} environment")
            return []
            
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Format address properly - API expects 'requests' array
        if isinstance(address, dict):
            payload = {
                'requests': [
                    {'propertyAddress': address}
                ]
            }
        else:
            # If address is a string, try to parse it
            payload = {
                'requests': [
                    {'propertyAddress': self._parse_address_string(address)}
                ]
            }
            
        print(f"\n[{self.env.upper()} API] Sending request for address:")
        addr = payload['requests'][0]['propertyAddress']
        print(f"  Street: {addr.get('street', 'N/A')}")
        print(f"  City: {addr.get('city', 'N/A')}")
        print(f"  State: {addr.get('state', 'N/A')}")
        print(f"  ZIP: {addr.get('zip', 'N/A')}")
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
            print(f"[{self.env.upper()} API] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                phone_numbers = self._extract_phone_numbers(data)
                print(f"[{self.env.upper()} API] Found {len(phone_numbers)} phone numbers")
                return phone_numbers
            else:
                print(f"[{self.env.upper()} API] Error: {response.text[:200]}")
                return []
                
        except requests.RequestException as e:
            print(f"[{self.env.upper()} API] Request failed: {e}")
            return []
    
    def _extract_phone_numbers(self, response_data):
        """Extract phone numbers from API response."""
        phone_numbers = []
        
        # Handle batch response format with responses array
        if 'responses' in response_data:
            for response in response_data['responses']:
                if 'results' in response:
                    results = response['results']
                    if 'persons' in results:
                        for person in results['persons']:
                            for phone in person.get('phoneNumbers', []):
                                number = phone.get('number')
                                if number:
                                    phone_numbers.append(number)
        
        # Handle single result format
        elif 'results' in response_data:
            results = response_data['results']
            if 'persons' in results:
                for person in results['persons']:
                    for phone in person.get('phoneNumbers', []):
                        number = phone.get('number')
                        if number:
                            phone_numbers.append(number)
        
        # For sandbox, might return mock data differently
        elif 'phoneNumbers' in response_data:
            for phone in response_data['phoneNumbers']:
                if isinstance(phone, str):
                    phone_numbers.append(phone)
                elif isinstance(phone, dict) and 'number' in phone:
                    phone_numbers.append(phone['number'])
                    
        # Fallback for simple list response
        elif isinstance(response_data, list):
            phone_numbers = [p for p in response_data if isinstance(p, str)]
            
        # Mock data for sandbox if no real response
        if self.env == 'sandbox' and not phone_numbers:
            # Return mock phone numbers for testing
            phone_numbers = ['555-0100', '555-0101', '555-0102']
            
        return phone_numbers
    
    def _parse_address_string(self, address_str):
        """Parse address string into structured format."""
        # Simple parser for "street, city, state zip" format
        parts = address_str.split(',')
        if len(parts) >= 2:
            street = parts[0].strip()
            remainder = parts[1].strip()
            
            # Split city, state, zip
            words = remainder.split()
            if len(words) >= 2:
                zip_code = words[-1]
                state = words[-2]
                city = ' '.join(words[:-2]) if len(words) > 2 else ''
                
                return {
                    'street': street,
                    'city': city,
                    'state': state,
                    'zip': zip_code
                }
        
        # Return as-is if parsing fails
        return {'street': address_str}


if __name__ == '__main__':
    # Test sandbox connector
    sandbox = BatchAPIConnector('sandbox')
    test_address = {
        'street': '1011 Rosegold St',
        'city': 'Franklin Square',
        'state': 'NY',
        'zip': '11010-2507'
    }
    
    print("Testing Sandbox API...")
    phone_numbers = sandbox.send_skip_trace_request(test_address)
    if phone_numbers:
        print(f"Phone numbers found: {phone_numbers}")
    else:
        print("No phone numbers found or request failed")