# Import packages
import logging
import pandas as pd
import requests
import urllib.parse
from credentials import credentials

class AmzService:

    # Get Sales data from AMZ
    # Getting LWA access token using the app credentials. Valid for 1 hour until it expires
    token_response = requests.post(
        "https://api.amazon.com/auth/o2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": credentials["refresh_token"],
            "client_id": credentials["lwa_app_id"],
            "client_secret": credentials["lwa_client_secret"],
        },
    )

    access_token = token_response.json()["access_token"]

    #NA endpoint
    endpoint = "https://sellingpartnerapi-na.amazon.com"
    marketplace_id = "ATVPDKIKX0DER"
    #US ATVPDKIKX0DER
    #CA A2EUQ1WTGCTBG2
    #MX
    
    def refreshAccessToken():
        self.access_token = token_reponse.json()["access_token"]

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
        