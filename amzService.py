# Import packages
import logging
import pandas as pd
import requests
import urllib.parse
from credentials import credentials

class AmzService:

    # Get Sales data from AMZ
    token_response = ''
    endpoint = ''
    marketplace_id = ''
    access_token = ''
    
    def __init__(self):
        # Getting LWA access token using the app credentials. Valid for 1 hour until it expires
        self.token_response = requests.post(
            "https://api.amazon.com/auth/o2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": credentials["refresh_token"],
                "client_id": credentials["lwa_app_id"],
                "client_secret": credentials["lwa_client_secret"],
            },
        )
        
        self.access_token = self.token_response.json()["access_token"]

        #NA endpoint
        self.endpoint = "https://sellingpartnerapi-na.amazon.com"
        self.marketplace_id = "ATVPDKIKX0DER"
        #US ATVPDKIKX0DER
        #CA A2EUQ1WTGCTBG2
        #MX
        
        
    
    def refreshAccessToken(self):
        self.access_token = self.token_reponse.json()["access_token"]

    # Postman: https://web.postman.co/workspace/My-Workspace~de12e46a-9cda-49b3-8350-c829508bdc38/request/15615900-7bc16135-483c-4bf8-9ed0-a07be598e199
    def getSales(self, asin, start, end, granularity):
        
        if self.access_token is None:
            print("access token is none. refreshing...")
            refreshAccessToken()
        
        request_params = {
            "marketplaceIds": self.marketplace_id,
        }
        if asin:
            request_params['asin'] = asin
        if start and end:
            interval = str(start) + 'T00:00:00-05:00--' + str(end) + 'T23:59:59-05:00'
            request_params['interval'] = interval
        if granularity:
            request_params['granularity'] = granularity

        logging.info('Calling AMZ for ' + str(request_params))

        try:
            sales = requests.get(
                self.endpoint + "/sales/v1/orderMetrics"
                + "?"
                + urllib.parse.urlencode(request_params),
                headers={
                    "x-amz-access-token": self.access_token,
                },
            )
        except:
            print("Something failed on the Amazon SP API service call")
        
        if(sales is not None and sales.status_code == 200):
            logging.info('AMZ SP API status code: ' + str(sales.status_code))
            df = pd.json_normalize(sales.json()['payload'])
            return df
        else:
            logging.error('AMZ SP API getSales() status code: '+ str(sales.status_code) + ' access token: ' + self.access_token + ' params: ' + str(request_params))
            raise ValueError(sales.status_code)
    



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
    def getFinancialEventGroups(self, start, end, eventGroupId, nextToken):
        
        request_params = {}
        if start:
            request_params['FinancialEventGroupStartedAfter'] = str(start) + 'T00:00:00-05:00'
        if end:
            request_params['FinancialEventGroupStartedBefore'] = str(end) + 'T23:59:59-05:00'
        if nextToken:
            request_params['NextToken'] = nextToken
        
        # Path variable
        eventGroupIdPath = ''
        if eventGroupId:
            eventGroupIdPath = '/' + eventGroupId +'/financialEvents'

        logging.info('Calling AMZ for ' + str(request_params))

        try:
            financialEventGroups = requests.get(
                self.endpoint + "/finances/v0/financialEventGroups"
                + eventGroupIdPath
                + "?"
                + urllib.parse.urlencode(request_params),
                headers={
                    "x-amz-access-token": self.access_token,
                },
            )
        except:
            print("Something failed on the Amazon SP API Financial Event Groups service call")
        
        if(financialEventGroups is not None and financialEventGroups.status_code == 200):
            logging.info('AMZ SP API Financial Events Groups status code: ' + str(financialEventGroups.status_code))
            df = pd.json_normalize(financialEventGroups.json()['payload'])
            return df
        else:
            print('AMZ SP API Financial Events Groups status code: '+ str(financialEventGroups.status_code))
            logging.error('AMZ SP API getFinancialEventGroups() status code: '+ str(financialEventGroups.status_code))
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