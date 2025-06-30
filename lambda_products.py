import json
import os
import requests
import boto3
from dotenv import load_dotenv
from kroger_access import get_kroger_access_token, get_product_url

# Load Kroger info from a .env 
load_dotenv()

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb',  region_name='us-west-1')
table = dynamodb.Table(os.environ['kroger_dynamodb'])
    
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
    
    if location_id:
        params['filter.locationId'] = location_id

    try:
        response = requests.get(get_product_url(), headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching Kroger products: {e}")
        raise


def lambda_handler(event, context):
    # Initial response values
    response_body = {}
    status_code = 200
    headers = {
        "Content-Type": "application/json"
    }

    try:
        if 'body' not in event or not event['body']:
            status_code = 400
            response_body = {"message": "Request body is missing or empty."}
            return {
                'statusCode': status_code,
                'headers': headers,
                'body': json.dumps(response_body)
            }

        # 2. Parse the JSON string from event['body'] into a Python dictionary
        request_body = json.loads(event['body'])

        # 3. Now, access the 'query' key from the *parsed* request_body dictionary
        query = request_body.get('query') # Use .get() for safe access

        # Ex: 'cookies, milk' -> ['cookies', 'milk']
        search_terms = [term.strip() for term in query.split(',') if term.strip()]

        all_products = []

        # Make multiple calls to Kroger API for each search term
        # https://developer.kroger.com/api-products/api/product-api-public#tag/Products/operation/productGet
        for term in search_terms:
            products_data = search_products(term).get('data', [])

            # Process and store data in DynamoDB based on product details
            for product in products_data:
                item = {
                    'productId': product.get('productId'),
                    'name': product.get('description'), 
                    'brand': product.get('brand'),
                    'price': product.get('items', [{}])[0].get('price') if product.get('items') else None,
                    'imageUrl': product.get('images', [{}])[0].get('sizes', [{}])[0].get('url') if product.get('images') else None,
                    'storeId': product.get('items', [{}])[0].get('fulfillment', {}).get('store', {}).get('id') if product.get('items') else None,
                    # Add location id
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
        print(f"Kroger API or network error: {e}") # Log the error to CloudWatch
        status_code = 502
        response_body = {"message": "Error communicating with Kroger API.", "error": str(e)}
    except ValueError as e:
        print(f"Configuration or data error: {e}")
        status_code = 500
        response_body = {"message": "Internal server configuration error.", "error": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        status_code = 500
        response_body = {"message": "An unexpected server error occurred.", "error": str(e)}
    finally:
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': json.dumps(response_body)
        }