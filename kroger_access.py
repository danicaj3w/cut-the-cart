import requests
import os
import time
import base64

# Replace with your credentials or set them in a .env file
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")

KROGER_TOKEN_URL = 'https://api.kroger.com/v1/connect/oauth2/token'
KROGER_PRODUCT_SEARCH_URL = 'https://api.kroger.com/v1/products'
KROGER_LOCATION_URL = 'https://api.kroger.com/v1/locations'

_kroger_access_token = None
_kroger_token_expiry_time = 0

def get_product_url():
    return KROGER_PRODUCT_SEARCH_URL

def get_location_url():
    return KROGER_LOCATION_URL

def get_kroger_access_token():
    global _kroger_access_token, _kroger_token_expiry_time

    # Check if the existing token is still valid
    if _kroger_access_token and time.time() < _kroger_token_expiry_time:
        print("Using cached Kroger access token.")
        return _kroger_access_token

    print("Requesting new Kroger access token...")
    try:
        # Base64 encode client ID and client secret
        auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded_auth}'
        }
        data = {
            'grant_type': 'client_credentials',
            'scope': 'product.compact'
        }

        response = requests.post(KROGER_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        _kroger_access_token = token_data['access_token']
        # Set expiry time a bit before actual expiration to be safe (e.g., 60 seconds buffer)
        _kroger_token_expiry_time = time.time() + token_data['expires_in'] - 60

        print("Successfully obtained new Kroger access token.")
        return _kroger_access_token

    except requests.exceptions.RequestException as e:
        print(f"Error getting Kroger access token: {e}")
        raise


# To test through CLI
# aws lambda invoke \
#   --function-name krogerProductsHandler \
#   --payload file://test_event.json \
#   output.json