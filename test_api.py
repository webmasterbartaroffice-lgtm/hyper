import requests
from requests.auth import HTTPBasicAuth
import json
import base64

# API credentials
CONSUMER_KEY = "ck_632cbd31da67a07adb33b6b848a98facd472b951"
CONSUMER_SECRET = "cs_1c8e450957778bd589844854a0007a98f84ed8e1"
BASE_URL = "https://hypermahdi.com/wp-json/wc/v3"

# Create basic auth header
credentials = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()

# Test API connection
print("Testing API connection...")

try:
    # Make a simple GET request to products endpoint
    url = f"{BASE_URL}/products"
    
    headers = {
        'Authorization': f'Basic {credentials}',
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    
    # Make the request
    print(f"Making request to: {url}")
    response = requests.get(
        url,
        headers=headers,
        verify=False,
        params={'per_page': 1}
    )
    
    # Print response details
    print(f"\nFull URL: {response.url}")
    print(f"Status Code: {response.status_code}")
    print("\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
    
    if response.status_code == 200:
        print("\nSuccess! First product data:")
        data = response.json()
        if data:
            print(json.dumps(data[0], indent=2))
    else:
        print("\nError Response:")
        print(response.text)

except Exception as e:
    print(f"Error occurred: {str(e)}") 