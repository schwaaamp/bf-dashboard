from datetime import date, timedelta
import pandas as pd
from SPAPI_Services.amzService import AmzService
from SPAPI_Services.searchTermsUtil import searchTerms

class CatalogService:
    
    
    def getSearchResults(self):
        service = AmzService()
        term = list(searchTerms.values())[0]
        print(term)
        result = service.getCatalogItems(term)
        numResults = result['numberOfResults']
        items = result['items'].values[0:1][0]
        
        df = pd.DataFrame()
        
        for item in items:
            asin = item['asin']
            itemName = item['summaries'][0]['itemName']
            brandName = item['summaries'][0]['brand']
            record = pd.DataFrame({"ASIN":[asin], "Item Name":[itemName], "Brand":[brandName]})
            df = pd.concat([df, record])
            
        return df