# Import packages
from dotenv import load_dotenv
import os
import logging
import pandas as pd
import requests
import urllib.parse
from sp_api.api import Sales
from sp_api.base import Granularity
from sp_api.base.marketplaces import Marketplaces



load_dotenv()  # loads variables from .env into environment

class AmzService:
    

    # Get Sales data from AMZ
    token_response = ''
    endpoint = "https://sellingpartnerapi-na.amazon.com"
    marketplace_id = "ATVPDKIKX0DER"
    access_token = ''
    
    """
    def __init__(self):
        # Getting LWA access token using the app credentials. Valid for 1 hour until it expires
        
        print(os.getenv("LWA_REFRESH_TOKEN"))
        print(os.getenv("LWA_APP_ID"))
        print(os.getenv("LWA_CLIENT_SECRET"))
        
        def __init__(self):
            # Request Amazon LWA token
            self.token_response = requests.post(
                "https://api.amazon.com/auth/o2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": os.getenv("LWA_REFRESH_TOKEN"),
                    "client_id": os.getenv("LWA_APP_ID"),
                    "client_secret": os.getenv("LWA_CLIENT_SECRET"),
                },
            )

        # Log the response for debugging
        print("Amazon token response:", self.token_response.status_code, self.token_response.text)

        # Safely extract token or raise an error
        if self.token_response.status_code == 200:
            self.access_token = self.token_response.json().get("access_token")
        else:
            raise Exception("Failed to obtain Amazon access token.")

        #NA endpoint
        self.endpoint = "https://sellingpartnerapi-na.amazon.com"
        self.marketplace_id = "ATVPDKIKX0DER"
        #US ATVPDKIKX0DER
        #CA A2EUQ1WTGCTBG2
        #MX
        
    """ 
    
    def refreshAccessToken(self):
        self.access_token = self.token_reponse.json()["access_token"]

    # Postman: https://web.postman.co/workspace/My-Workspace~de12e46a-9cda-49b3-8350-c829508bdc38/request/15615900-7bc16135-483c-4bf8-9ed0-a07be598e199
    def getSales(self, asin, start, end, granularity):
        # Ensure access token is available
        """
        if not self.access_token:
            logging.warning("Access token is None. Refreshing...")
            self.refreshAccessToken()  # Assumes this method exists
"""
        # Build request parameters
        params = {"marketplaceIds": self.marketplace_id}
        interval = ''
        if asin:
            params["asin"] = asin
        if start and end:
            interval = f"{start}T00:00:00Z--{end}T23:59:59Z"
            interval="2024-09-01T00:00:00-07:00–2024-09-04T00:00:00-07:00"
            print(interval)
            params["interval"] = f"{start}T00:00:00-05:00--{end}T23:59:59-05:00"
        if granularity:
            params["granularity"] = granularity

        url = f"{self.endpoint}/sales/v1/orderMetrics"
        headers = {"x-amz-access-token": self.access_token}

        logging.info(f"Calling Amazon SP API with params: {params}")

        try:
            print(interval)
            sales_api = Sales(marketplace=Marketplaces.US)
            response = sales_api.get_order_metrics(
                granularity=Granularity.TOTAL,
                granularityTimeZone='US/Eastern'
                #asin=asin,
                interval=interval,
            )
            
            print(response)
            return response
            
            #response = requests.get(url, headers=headers, params=params)
            #response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Amazon SP API request failed: {e}")
            raise RuntimeError("Amazon SP API call failed") from e

        logging.info(f"Amazon SP API response status: {response.status_code}")

        try:
            payload = response.json().get("payload", [])
            df = pd.json_normalize(payload)
            return df
        except (ValueError, KeyError) as e:
            logging.error(f"Failed to parse API response: {e}")
            raise
        



    # believe this needs to get the financial events for the active financial events group id
    # this might be useful for figuring out what i made yesterday

    def getFinancialEvents(self, start, end):
        request_params = {}
        if start:
            request_params['PostedAfter'] = str(start) + 'T00:00:00-05:00'
        if end:
            request_params['postedBefore'] = str(end) + 'T23:59:59-05:00'

        logging.info('Calling AMZ for ' + str(request_params))

        try:
            financialEvents = requests.get(
                self.endpoint + "/finances/v0/financialEvents"
                + "?"
                + urllib.parse.urlencode(request_params),
                headers={
                    "x-amz-access-token": self.access_token,
                },
            )
        except:
            print("Something failed on the Amazon SP API list Financial Events service call")
        
        if(financialEvents is not None and financialEvents.status_code == 200):
            logging.info('AMZ SP API list Financial Events status code: ' + str(financialEvents.status_code))
            df = pd.json_normalize(financialEvents.json()['payload'])
            return df
        else:
            print('AMZ SP API list Financial Events status code: '+ str(financialEvents.status_code))
            logging.error('AMZ SP API getFinancialEvents() status code: '+ str(financialEvents.status_code))
            return pd.DataFrame()
    
    
    # This is a multi-use function. It retrieves FinancialEventGroups and also orders that are part of a specific FinancialEventGroupId.
    # The latter requires a path variable (eventGroupId) and paginates results every 100 orders via NextToken
    def getFinancialEventGroups(self, start=None, end=None, eventGroupId=None, nextToken=None):
        # Build request parameters
        params = {}
        if start:
            params["FinancialEventGroupStartedAfter"] = f"{start}T00:00:00-05:00"
        if end:
            params["FinancialEventGroupStartedBefore"] = f"{end}T23:59:59-05:00"
        if nextToken:
            params["NextToken"] = nextToken

        # Determine endpoint path
        event_group_path = f"/{eventGroupId}/financialEvents" if eventGroupId else ""

        url = f"{self.endpoint}/finances/v0/financialEventGroups{event_group_path}"
        headers = {"x-amz-access-token": self.access_token}

        logging.info(f"Calling Amazon SP API Financial Event Groups with params: {params}")

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            payload = response.json().get("payload", [])
            df = pd.json_normalize(payload)
            logging.info(f"AMZ SP API Financial Event Groups success. Status code: {response.status_code}")
            return df

        except requests.exceptions.RequestException as e:
            logging.error(f"Amazon SP API Financial Event Groups request failed: {e}")
        except ValueError as e:
            logging.error(f"Error parsing JSON response: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in getFinancialEventGroups: {e}")

        # On failure, return empty DataFrame
        return pd.DataFrame()






    def getInventory(self):
        request_params = {
            "marketplaceIds": self.marketplace_id,
            "granularityType": "Marketplace",
            "granularityId": "1",
            "details": "true",
        }

        logging.info('Calling AMZ for ' + str(request_params))

        try:
            inventorySummary = requests.get(
                self.endpoint + "/fba/inventory/v1/summaries"
                + "?"
                + urllib.parse.urlencode(request_params),
                headers={
                    "x-amz-access-token": self.access_token,
                },
            )
        except:
            print("Something failed on the Amazon SP API Inventory service call")
        
        if(inventorySummary is not None and inventorySummary.status_code == 200):
            logging.info('AMZ SP API list inventory status code: ' + str(inventorySummary.status_code))
            df = pd.json_normalize(inventorySummary.json()['payload'])
            return df
        else:
            print('AMZ SP API list inventory status code: '+ str(inventorySummary.status_code))
            logging.error('AMZ SP API getInventory() status code: '+ str(inventorySummary.status_code))
            return pd.DataFrame()
        
        
        
        
    def getCatalogItems(self, keywords):
        request_params = {
            "marketplaceIds": self.marketplace_id,
            "keywords": keywords,
        }

        logging.info('Calling AMZ for ' + str(request_params))

        try:
            inventorySummary = requests.get(
                self.endpoint + "/catalog/2022-04-01/items"
                + "?"
                + urllib.parse.urlencode(request_params),
                headers={
                    "x-amz-access-token": self.access_token,
                },
            )
        except:
            print("Something failed on the Amazon SP API Catalog service call")
        
        if(inventorySummary is not None and inventorySummary.status_code == 200):
            logging.info('AMZ SP API searchCatalogItems status code: ' + str(inventorySummary.status_code))
            df = pd.json_normalize(inventorySummary.json())
            return df
        else:
            print('AMZ SP API searchCatalogItems status code: '+ str(inventorySummary.status_code))
            logging.error('AMZ SP API getInventory() status code: '+ str(inventorySummary.status_code))
            return pd.DataFrame()
        
        
        
        
        
    def getPricing(self, asins):
        request_params = {
            "MarketplaceId": self.marketplace_id,
            "Asins": asins, #list of up to 20 asins
            "ItemType":'Asin',
            
        }

        logging.info('Calling AMZ for ' + str(request_params))

        try:            
            pricing = requests.get(
                self.endpoint + "/products/pricing/v0/competitivePrice"
                + "?"
                + urllib.parse.urlencode(request_params),
                headers={
                    "x-amz-access-token": self.access_token,
                },
            )
        except:
            print("Something failed on the Amazon SP API Price service call")
        
        if(pricing is not None and pricing.status_code == 200):
            logging.info('AMZ SP API getPricing status code: ' + str(pricing.status_code))
            df = pd.json_normalize(pricing.json()['payload'])
            return df
        else:
            print('AMZ SP API getPricing status code: '+ str(pricing.status_code) + pricing.reason)
            logging.error('AMZ SP API getPricing() status code: '+ str(pricing.status_code) + pricing.reason)
            return pd.DataFrame()