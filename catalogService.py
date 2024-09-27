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
                record = pd.DataFrame({"Query":[term],"ASIN":[asin], "Item Name":[itemName], "Brand":[brandName], "Ranking":[ranking]})
                df = pd.concat([df, record])
        
        # remove dupes in asin list
        asins = list(set(asins))
        
        # Call pricing service to get pricing for the asins[]. Append to df before returning
        pricingDf = pricingService.getPricingByAsin(asins)
        
        #iterate through df, find price from pricingDf, add values to new dataframe
        df.reset_index()
        pricingDf.reset_index()
        prices = []
        categoryRankings = []
        listingLinks = []
        
        for index, row in df.iterrows():
            record = pricingDf.loc[pricingDf['ASIN'] == row['ASIN']]
            price = record['ListingPrice'][0]
            categoryRank = record['SalesRanking']
            prices.append(price)
            categoryRankings.append(categoryRank)
            #add link to listing as column
            listingLinks.append('https://www.amazon.com/dp/' + row['ASIN'])
        
        df['Listing Price'] = prices
        df['Category Rank'] = categoryRankings
        df['Link'] = listingLinks
        
        df_list = []
        for term in searchTerms.values():
            trimmedDf = df[df['Query'] == term]
            df_list.append(trimmedDf)
        return df_list
    
    def getOrganicSearchRanking(self, df, term):
        return np.where(ASIN == term)
        