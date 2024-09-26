from amzService import AmzService

class PricingService:
    
    
    def getPricingByAsin(self, asins):
        # Need to split asins into lists of 20 then combine the results
        amzService = AmzService()
        a = ''
        for asin in asins:
            a += asin + ','
        
        a = a[:-1]
        print(a)
        df = amzService.getPricing(a)
        print(df)