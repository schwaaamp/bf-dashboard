from datetime import date, timedelta
import pandas as pd
from SPAPI_Services.amzService import AmzService
from SPAPI_Services.salesService import SalesService

# Test getting inventory
service = AmzService()
salesService = SalesService()
inventoryDf = service.getInventory()
df = pd.DataFrame()


num_weeks=8
# Should we go 8 weeks from today or from last week? Are we getting full weeks for doing averages?
eight_weeks = date.today() - timedelta(weeks=num_weeks)
eight_start = eight_weeks - timedelta(days=eight_weeks.weekday())

# If there are multiple marketplaces, need to adjust this first line
for summ in inventoryDf.values[0:1][0]:
    if isinstance(summ, list):
        for item in summ:
            asin = item['asin']
            available = item['inventoryDetails']['fulfillableQuantity']
            inbound = item['inventoryDetails']['inboundWorkingQuantity'] + item['inventoryDetails']['inboundShippedQuantity'] + item['inventoryDetails']['inboundReceivingQuantity']
            fcTransfer = item['inventoryDetails']['reservedQuantity']['pendingTransshipmentQuantity']
            if(available > 0 or inbound > 0 or fcTransfer > 0):
                # Get 8 week average per ASIN
                df_eight = salesService.getSalesByWeek(asin, eight_start, eight_start + timedelta(weeks=num_weeks))
                df_eight['ASIN'] = asin
                week_avg = (df_eight.groupby(['ASIN'], observed=True)['Unit Count'].sum() / num_weeks)
                avgDf = pd.DataFrame({'ASIN': [asin], 'Available':[available], 'Total Inbound':[inbound], 'Total On Hand':[available + inbound + fcTransfer], 'Week Average':[week_avg.values[0]], 'Weeks On Hand':[(available + inbound + fcTransfer) / week_avg.values[0]]})
                df = pd.concat([df, avgDf])


print(df)
# If weeks on hand < 6, ship (draw attention)