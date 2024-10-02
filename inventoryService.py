
from datetime import date, timedelta
import pandas as pd
import time
from amzService import AmzService
from salesService import SalesService

class InventoryService:

    service = AmzService()
    salesService = SalesService()

    def getInventoryNeeds(self):
        inventoryDf = self.service.getInventory()
        num_weeks=8
        eight_weeks = date.today() - timedelta(weeks=num_weeks)
        eight_start = eight_weeks - timedelta(days=eight_weeks.weekday())
        df = pd.DataFrame()

        # If there are multiple marketplaces, need to adjust this first line
        for summ in inventoryDf.values[0:1][0]:
            if isinstance(summ, list):
                for item in summ:
                    asin = item['asin']
                    # Some ASINs are repeated in AMZ inventory due to multiple SKUs; we only need one
                    if asin not in df.values:
                        available = item['inventoryDetails']['fulfillableQuantity']
                        inbound = item['inventoryDetails']['inboundWorkingQuantity'] + item['inventoryDetails']['inboundShippedQuantity'] + item['inventoryDetails']['inboundReceivingQuantity']
                        fcTransfer = item['inventoryDetails']['reservedQuantity']['pendingTransshipmentQuantity']
                        if(available > 0 or inbound > 0 or fcTransfer > 0):
                            # Get 8 week average per ASIN
                            df_eight = self.salesService.getSalesByWeek(asin, eight_start, eight_start + timedelta(weeks=num_weeks))
                            df_eight['ASIN'] = asin
                            week_avg = (df_eight.groupby(['ASIN'], observed=True)['Unit Count'].sum() / num_weeks)
                            weeks_on_hand = float(format((available + inbound + fcTransfer) / week_avg.values[0], '.1f'))
                            avgDf = pd.DataFrame({'ASIN': [asin], 'Available':[available], 'Total Inbound':[inbound], 'Total On Hand':[available + inbound + fcTransfer], 'Week Average':[week_avg.values[0]], 'Weeks On Hand':[weeks_on_hand]})
                            df = pd.concat([df, avgDf])

        return(df.sort_values(by=['Weeks On Hand']))