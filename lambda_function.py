import json
import os
import base64
import requests
import boto3
import time
from dotenv import load_dotenv

# Load Kroger info from a .env 
load_dotenv()

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',  region_name='us-west-1')
table = dynamodb.Table(os.environ['kroger_dynamodb'])

# Replace with your credentials or set them in a .env file
CLIENT_ID = os.getenv("CLIENT_ID", "cut-the-cart-bbc69jn8")
CLIENT_SECRET=os.getenv("CLIENT_SECRET", "igboO52f7OJ81C7dKT3oi1HBZiRt4h0BEdQYJ2Fs")
KROGER_TOKEN_URL = 'https://api.kroger.com/v1/connect/oauth2/token'
KROGER_PRODUCT_SEARCH_URL = 'https://api.kroger.com/v1/products'

_kroger_access_token = None
_kroger_token_expiry_time = 0 # Unix timestamp

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


def search_products(search_query,location_id=None,limit=20):
    access_token = get_kroger_access_token()
    if not access_token:
        raise Exception("Could not obtain Kroger access token.")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filter.term': search_query,
        'filter.limit': limit
    }
    
    if location_id: # ? What does this do?
        params['filter.locationId'] = location_id

    try:
        response = requests.get(KROGER_PRODUCT_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching Kroger products: {e}")
        raise


def lambda_function(event, context):
    # Initial response values
    response_body = {}
    status_code = 200
    headers = {
        "Content-Type": "application/json"
    }

    try:

        # Get the user's search query
        query_string_parameters = event.get('queryStringParameters')
        if not query_string_parameters or 'query' not in query_string_parameters:
            status_code = 400
            response_body = {"message": "Missing 'query' parameter."}
            return {
                'statusCode': status_code,
                'headers': headers,
                'body': json.dumps(response_body)
            }

        # Extract query terms
        # Ex: 'cookies, milk' -> ['cookies', 'milk']
        raw_query = query_string_parameters['query']
        search_terms = [term.strip() for term in raw_query.split(',') if term.strip()]

        all_products = []

        # Make multiple calls to Kroger API for each search term
        # https://developer.kroger.com/api-products/api/product-api-public#tag/Products/operation/productGet
        for term in search_terms:
            kroger_api_params = {
                'filter.term': term,
                'filter.limit': 20 
                # 'filter.locationId': 'YOUR_KROGER_STORE_ID' # Uncomment and replace if you want to filter by specific store
            }

            product_headers = {
                'Authorization': f'Bearer {access_token}'
            }

            # Make a GET request to the Kroger product search URL
            product_response = requests.get(KROGER_PRODUCT_SEARCH_URL, headers=product_headers, params=kroger_api_params)
            product_response.raise_for_status()
            products_data = product_response.json().get('data', [])

            # Process and store data in DynamoDB based on product details
            for product in products_data:
                item = {
                    'productId': product.get('productId'),
                    'name': product.get('description'), 
                    'brand': product.get('brand'),
                    # Extract price from 'items' list
                    'price': product.get('items', [{}])[0].get('price') if product.get('items') else None,
                    # Extract image URL from 'images' list
                    'imageUrl': product.get('images', [{}])[0].get('sizes', [{}])[0].get('url') if product.get('images') else None,
                    # Extract store ID from the first item's fulfillment details
                    'storeId': product.get('items', [{}])[0].get('fulfillment', {}).get('store', {}).get('id') if product.get('items') else None,
                    # Add a timestamp for when the data was last updated/fetched
                    'lastUpdated': boto3.util.isoformat(boto3.util.current_time()), # ISO 8601 timestamp for sorting/filtering
                }

                # Store item into DynamoDB table
                table.put_item(Item=item)
                all_products.append(item)

        # Return the list of products to the client
        response_body = {
            "message": "Products fetched and stored successfully.",
            "products": all_products
        }

    except requests.exceptions.RequestException as e:
        # Catch errors specifically related to HTTP requests (network issues, bad API responses).
        print(f"Kroger API or network error: {e}") # Log the error to CloudWatch
        status_code = 502 # 502 Bad Gateway indicates an issue with an upstream server (Kroger API)
        response_body = {"message": "Error communicating with Kroger API.", "error": str(e)}
    except ValueError as e:
        # Catch errors related to invalid configuration or data (e.g., missing access token).
        print(f"Configuration or data error: {e}")
        status_code = 500 # Internal Server Error for issues within our Lambda logic/config
        response_body = {"message": "Internal server configuration error.", "error": str(e)}
    except Exception as e:
        # Catch any other unexpected errors. This is a general fallback.
        print(f"An unexpected error occurred: {e}")
        status_code = 500
        response_body = {"message": "An unexpected server error occurred.", "error": str(e)}
    finally:
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': json.dumps(response_body)
        }
    
if __name__ == '__main__':
    print(search_products('milk'))
#     mock_event = {'search_query': 'milk'} 

#     result = lambda_function(mock_event, None)
#     print(result)

    # # Simulate Lambda event
    # mock_event = {}  # Put test data here if needed
    # mock_context = None
    # result = lambda_handler(mock_event, mock_context)
    # print(result)