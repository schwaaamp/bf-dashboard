from amzService import AmzService
import pandas as pd

class PricingService:
    
    
    def getPricingByAsin(self, asins):
       # Need to split asins into lists of 20 then combine the results
        amzService = AmzService()
        pricingDf = pd.DataFrame()

        for i in range(0, len(asins), 20):
            a = asins[i:i+20] #retrieves sublist of up to 20 asins from main list
            
            # convert above list of 20 to string param and call service
            asin_param = ''
            for asin in a:
                asin_param += asin + ','

            asin_param = asin_param[:-1]   #remove trailing ,
            df = amzService.getPricing(asin_param)
            df.columns = ['ASIN', 'Status', 'Competitive Pricing', 'NumberOfOfferListings', 'MarketplaceId', 'IdentifiersAsin', 'SalesRankings']
            slimDf = df[['ASIN', 'Status', 'Competitive Pricing', 'SalesRankings']].copy()
                
            #whittle df down to fields we actually want
            recordList = slimDf.values[0:20]
            for record in recordList:
                asin = record[0]
                status = record[1]
                listingPrice = ''
                
                for p in range(len(record[2])):
                    condition =  record[2][p]['condition']
                    if condition == 'New':
                        listingPrice = str(record[2][p]['Price']['ListingPrice']['Amount'])
                        
                
                categoryRank = record[3][1]['Rank']
                tempDf = pd.DataFrame({'ASIN':pd.Series(asin, dtype='str'),
                                    'Status':pd.Series(status, dtype='str'),
                                    'ListingPrice':pd.Series(listingPrice, dtype='float'),
                                    'SalesRanking':pd.Series(categoryRank, dtype='int')})
                pricingDf = pd.concat([pricingDf, tempDf])
            
        pricingDf.drop_duplicates() 
        return pricingDf