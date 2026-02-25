import os
import requests
import datetime
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import urlencode
from aws_requests_auth.aws_auth import AWSRequestsAuth

load_dotenv()

_cached_token = None
_token_expiry = None

# Step 1: Get access token from LWA
def get_lwa_access_token():
    global _cached_token, _token_expiry

    if _cached_token and _token_expiry and datetime.datetime.now() < _token_expiry:
        return _cached_token

    response = requests.post(
        "https://api.amazon.com/auth/o2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
            "client_id": os.getenv("LWA_APP_ID"),
            "client_secret": os.getenv("LWA_CLIENT_SECRET"),
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    payload = response.json()
    _cached_token = payload["access_token"]
    _token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=payload["expires_in"] - 60)
    return _cached_token

# Step 2: Sign and send Sales API request
def getSales(asin, start_date, end_date, granularity):
    access_token = get_lwa_access_token()

    region = "us-east-1"
    service = "execute-api"
    host = "sellingpartnerapi-na.amazon.com"
    endpoint = f"https://{host}/sales/v1/orderMetrics"

    params = {
        "marketplaceIds": "ATVPDKIKX0DER",
        "asin": asin,
        "interval": f"{start_date}T00:00:00Z--{end_date}T23:59:59Z",
        "granularity": granularity,
    }

    auth = AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        aws_token=None,  # If using session tokens
        aws_host=host,
        aws_region=region,
        aws_service=service,
    )

    headers = {
        "x-amz-access-token": access_token,
        "Content-Type": "application/json",
    }

    response = requests.get(endpoint, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    #return response.json()
    payload = response.json().get("payload", [])
    df = pd.json_normalize(payload)
    return df


"""============================================"""
    
    

# This is a multi-use function. It retrieves FinancialEventGroups and also orders that are part of a specific FinancialEventGroupId.
# The latter requires a path variable (eventGroupId) and paginates results every 100 orders via NextToken
def getFinancialEventGroups(start=None, end=None, eventGroupId=None, nextToken=None):
    
    access_token = get_lwa_access_token()
    
    event_group_path = f"/{eventGroupId}/financialEvents" if eventGroupId else ""

    region = "us-east-1"
    service = "execute-api"
    host = "sellingpartnerapi-na.amazon.com"
    endpoint = f"https://{host}/finances/v0/financialEventGroups{event_group_path}"
    
    
    # Build request parameters
    params = {}
    if start:
        params["FinancialEventGroupStartedAfter"] = f"{start}T00:00:00-05:00"
    if end:
        params["FinancialEventGroupStartedBefore"] = f"{end}T23:59:59-05:00"
    if nextToken:
        params["NextToken"] = nextToken

    auth = AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        aws_token=None,  # If using session tokens
        aws_host=host,
        aws_region=region,
        aws_service=service,
    )

    headers = {
        "x-amz-access-token": access_token,
        "Content-Type": "application/json",
    }
    
    
    response = requests.get(endpoint, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    #return response.json()
    payload = response.json().get("payload", [])
    df = pd.json_normalize(payload)
    return df




def getInventory():
    
    access_token = get_lwa_access_token()

    region = "us-east-1"
    service = "execute-api"
    host = "sellingpartnerapi-na.amazon.com"
    endpoint = f"https://{host}/fba/inventory/v1/summaries?"

    params = {
        "marketplaceIds": "ATVPDKIKX0DER",
        "granularityType": "Marketplace",
        "granularityId": "1",
        "details": "true",
    }

    auth = AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        aws_token=None,  # If using session tokens
        aws_host=host,
        aws_region=region,
        aws_service=service,
    )

    headers = {
        "x-amz-access-token": access_token,
        "Content-Type": "application/json",
    }

    response = requests.get(endpoint, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    #return response.json()
    df = pd.json_normalize(response.json()['payload'])
    return df
    
    
    
    
def getCatalogItems(keywords):
    
    access_token = get_lwa_access_token()

    region = "us-east-1"
    service = "execute-api"
    host = "sellingpartnerapi-na.amazon.com"
    endpoint = f"https://{host}/catalog/2022-04-01/items?"

    params = {
        "marketplaceIds": "ATVPDKIKX0DER",
        "keywords": keywords,
    }

    auth = AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        aws_token=None,  # If using session tokens
        aws_host=host,
        aws_region=region,
        aws_service=service,
    )

    headers = {
        "x-amz-access-token": access_token,
        "Content-Type": "application/json",
    }

    response = requests.get(endpoint, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    #return response.json()
    df = pd.json_normalize(response.json())
    return df
    
    
    
    
    
    
    
    
def getPricing(asins):
    access_token = get_lwa_access_token()

    region = "us-east-1"
    service = "execute-api"
    host = "sellingpartnerapi-na.amazon.com"
    endpoint = f"https://{host}/products/pricing/v0/competitivePrice?"

    params = {
        "MarketplaceId": "ATVPDKIKX0DER",
        #"Asins": ','.join(asins), #list of up to 20 asins
        "Asins": asins,
        "ItemType": "Asin",
    }

    auth = AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        aws_token=None,  # If using session tokens
        aws_host=host,
        aws_region=region,
        aws_service=service,
    )

    headers = {
        "x-amz-access-token": access_token,
        "Content-Type": "application/json",
    }

    response = requests.get(endpoint, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    #return response.json()
    df = pd.json_normalize(response.json()['payload'])
    return df



def getFbaShipments(asins):
    access_token = get_lwa_access_token()

    region = "us-east-1"
    service = "execute-api"
    host = "sellingpartnerapi-na.amazon.com"
    endpoint = f"https://{host}/fba/inbound/v0/shipments?"

    params = {
        "MarketplaceId": "ATVPDKIKX0DER",
        #"Asins": ','.join(asins), #list of up to 20 asins
        "Asins": asins,
        "ItemType": "Asin",
    }

    auth = AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        aws_token=None,  # If using session tokens
        aws_host=host,
        aws_region=region,
        aws_service=service,
    )

    headers = {
        "x-amz-access-token": access_token,
        "Content-Type": "application/json",
    }

    response = requests.get(endpoint, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    #return response.json()
    df = pd.json_normalize(response.json()['payload'])
    return df
