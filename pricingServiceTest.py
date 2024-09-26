from pricingService import PricingService
from amzService import AmzService
import pandas as pd

# Need to split asins into lists of 20 then combine the results
amzService = AmzService()
pricingDf = pd.DataFrame()
results = dict()

for i in range(0, len(asins), 20):
    a = asins[i:i+20] #retrieves sublist of up to 20 asins from main list
    
    # convert above list of 20 to string param and call service
    asin_param = ''
    for asin in a:
        asin_param += asin + ','

    asin_param = asin_param[:-1]   #remove trailing ,
    df = amzService.getPricing(asin_param)
    
    #whittle df down to fields we actually want
    for record in df:
        #asin = record['ASIN']
        #print(asin)
        print('looping')
    
    #merge all service calls into one df - do we want this or key value pair?
    pricingDf = pd.concat([pricingDf, df])
    

print(pricingDf)