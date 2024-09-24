from datetime import date, timedelta
import pandas as pd
import numpy as np
from SPAPI.amzService import AmzService
from SPAPI.searchTermsUtil import searchTerms

class CatalogService:
    
    
    def getSearchResults(self):
        service = AmzService()
        df = pd.DataFrame()
        
        for term in searchTerms.values():
            ranking = 0
            result =  service.getCatalogItems(term)
            numResults = result['numberOfResults']
            items = result['items'].values[0:1][0]
        
            for item in items:
                ranking = ranking+1
                asin = item['asin']
                itemName = item['summaries'][0]['itemName']
                brandName = item['summaries'][0]['brand']
                record = pd.DataFrame({"ASIN":[asin], "Item Name":[itemName], "Brand":[brandName], "Ranking":[ranking]})
                df = pd.concat([df, record])
            
        return df
    
    def getOrganicSearchRanking(self, df, term):
        #return df.loc[df.isin([term]).any(axis=1)].index.tolist()
        return np.where(ASIN == term)
        