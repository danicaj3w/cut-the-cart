import json
import requests
from dotenv import load_dotenv
from kroger_access import get_kroger_access_token, get_location_url

def get_nearest_location(location_query):
    access_token = get_kroger_access_token()
    if not access_token:
        raise Exception("Could not obtain Kroger access token.")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'filter.zipCode.near': location_query,
    }

    try:
        response = requests.get(get_location_url(), headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching Kroger locations: {e}")
        raise


def lambda_handler(event, context):
    response_body = {}
    status_code = 200
    headers = {
        "Content-Type": "application/json"
    }

    try:
        zipcode = event.get("zipCode")

        if zipcode is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing 'zipcode' in the event payload."})
            }

        nearest_location = get_nearest_location(zipcode)

        if nearest_location:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Nearest Kroger location found successfully.",
                    "location": {
                        "id": nearest_location.get("locationId"),
                        "name": nearest_location.get("name"),
                        "address": nearest_location.get("address", {}).get("addressLine1"),
                        "city": nearest_location.get("address", {}).get("city"),
                        "state": nearest_location.get("address", {}).get("state"),
                        "zipCode": nearest_location.get("address", {}).get("zipCode"),
                    }
                })
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No nearest Kroger location found for the given coordinates."})
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