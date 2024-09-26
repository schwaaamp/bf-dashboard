from datetime import date, timedelta
import pandas as pd
import numpy as np
from amzService import AmzService
from pricingService import PricingService
from utils.searchTerms import searchTerms

class CatalogService:
    
    
    def getSearchResults(self):
        service = AmzService()
        pricingService = PricingService()
        df = pd.DataFrame()
        asins = []
        
        for term in searchTerms.values():
            ranking = 0
            result =  service.getCatalogItems(term)
            numResults = result['numberOfResults']
            items = result['items'].values[0:1][0]
        
            for item in items:
                ranking = ranking+1
                asin = item['asin']
                asins.append(asin)
                itemName = item['summaries'][0]['itemName']
                brandName = item['summaries'][0]['brand']
                record = pd.DataFrame({"ASIN":[asin], "Item Name":[itemName], "Brand":[brandName], "Ranking":[ranking]})
                df = pd.concat([df, record])
        
        # Call pricing service to get pricing for the asins[]. Append to df before returning
        #prices = pricingService.getPricingByAsin(asins)
        #print('PRICING DF: ' + prices)
        
        return df
    
    def getOrganicSearchRanking(self, df, term):
        return np.where(ASIN == term)
        