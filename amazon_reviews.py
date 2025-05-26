import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from datetime import datetime
from credentials import credentials
import json

# ----------------------
# CONFIGURATION
# ----------------------
CLIENT_ID = credentials['lwa_app_id']
CLIENT_SECRET = credentials['lwa_client_secret']
REFRESH_TOKEN = credentials['refresh_token']

AWS_ACCESS_KEY = credentials['aws_access_key']
AWS_SECRET_KEY = credentials['aws_secret_key']
AWS_SESSION_TOKEN = None  # Only needed if using temporary credentials

REGION = 'us-east-1'
SP_API_HOST = 'sellingpartnerapi-na.amazon.com'


# ----------------------
# AUTH FUNCTIONS
# ----------------------
def get_lwa_access_token(client_id, client_secret, refresh_token):
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']


def sign_request(method, url, region, service, access_key, secret_key, session_token, headers, body):
    request = AWSRequest(method=method, url=url, data=body, headers=headers)
    credentials = Credentials(access_key, secret_key, session_token)
    signer = SigV4Auth(credentials, service, region)
    signer.add_auth(request)
    return request.prepare()


# ----------------------
# API CALL
# ----------------------
def get_product_reviews(asin, access_token, aws_keys):
    SP_API_HOST = 'sellingpartnerapi-na.amazon.com'
    endpoint = "https://"+SP_API_HOST+"/products/2020-12-01/reviews?asin={asin}"

    headers = {
        'host': SP_API_HOST,
        'x-amz-access-token': access_token,
        'content-type': 'application/json'
    }

    signed_request = sign_request(
        method='GET',
        url=endpoint,
        region=REGION,
        service='execute-api',
        access_key=aws_keys['access_key'],
        secret_key=aws_keys['secret_key'],
        session_token=aws_keys.get('session_token'),
        headers=headers,
        body=None
    )

    response = requests.request(
        method='GET',
        url=endpoint,
        headers=dict(signed_request.headers)
    )

    if response.status_code == 403:
        print("❌ Access denied. You may not have permission to access this endpoint.")
    response.raise_for_status()
    return response.json()


# ----------------------
# MAIN
# ----------------------
if __name__ == "__main__":
    asin = 'B08FY29Z7L'  # Change this to your ASIN

    aws_keys = {
        'access_key': AWS_ACCESS_KEY,
        'secret_key': AWS_SECRET_KEY,
        'session_token': AWS_SESSION_TOKEN
    }

    try:
        print("🔐 Getting LWA access token...")
        access_token = get_lwa_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

        print(f"📦 Fetching reviews for ASIN: {asin}...")
        reviews = get_product_reviews(asin, access_token, aws_keys)

        print("✅ Reviews fetched successfully:")
        print(json.dumps(reviews, indent=2))

    except requests.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
    except Exception as ex:
        print(f"❌ Unexpected Error: {ex}")
