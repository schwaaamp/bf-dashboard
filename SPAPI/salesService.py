import csv
import datetime
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from SPAPI.amzService import AmzService
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames


class SalesService:


    def getSales(self, asin, start, end, granularity):
        if granularity == 'Day':
            return self.getSalesByDay(asin, start, end)
        elif granularity == 'Week' or granularity == 'Month':
            return self.getSalesByWeek(asin, start, end)
        else:
            print('Unexpected granularity type')
            
    # Moved this from app.py
    # Look into refactoring
    def getSalesForDatesByAsin(self, start, end, asin, granularity):
        start = date.fromisoformat(start)
        end = date.fromisoformat(end)
        df = pd.DataFrame()
        if asin != 'All':
            df = self.getSales(asin, start, end, granularity)
            df['ASIN'] = asin
            df['Product'] = asinNames.get(asin)
        else:
            for asin in asinSkuMapper.keys():
                tempDf = self.getSales(asin, start, end, granularity)
                tempDf['ASIN'] = asin
                tempDf['Product'] = asinNames.get(asin)
                df = pd.concat([df, tempDf])
        
        return df
        

    
    # Check if file exists for each asin and date range
    # If so, retrieve values from file
    # If not, call AMZ SP API for sales and create file
    # Only add AMZ SP API sales to file if it is not today (incomplete)
    def getSalesByDay(self, asin, start, end):

        sku = asinSkuMapper.get(asin)
        sales_file = Path('csvs/' + sku + '.csv')

        if sales_file.is_file():
            f = pd.read_csv(sales_file, delimiter='\t')
            delta = end - start
            results = pd.DataFrame()

            for i in range(delta.days + 1):
                day = str(start + datetime.timedelta(days=i))
                if day in f['Date'].values:
                    record = f.loc[f['Date'] == day]
                    results = pd.concat([results, record])
                else:
                    # Only want to call Amazon if day is > first date in the file (when item launched)
                    if day > f['Date'].iloc[0]:
                        df = self.getSalesFromAmz(asin, day, day, 'Day')
                        df_clean = pd.DataFrame({"Date":df['interval'].str.slice(0,10), "Unit Count":df['unitCount'], "Order Count":df['orderCount'], "Sales":df['totalSales.amount']})
                        results = pd.concat([results, df_clean])
                        if day != str(date.today()):
                            print('Adding ' + day + ' to ' + str(sales_file))
                            # mode='a' appends this dataframe to the existing file
                            df_clean.to_csv('csvs/' + sku + '.csv', sep='\t', encoding='utf-8', index=False, header=False, mode='a')
            return results
        else:
            print('File does not exist')
            # Create sales.csv file
            df = self.getSalesFromAmz(asin, start, end, 'Day')
            df_clean = pd.DataFrame({"Date":df['interval'].str.slice(0,10), "Unit Count":df['unitCount'], "Order Count":df['orderCount'], "Sales":df['totalSales.amount']})
            print(df_clean)
            df_clean.to_csv('csvs/' + sku + '.csv', sep='\t', encoding='utf-8', index=False, header=True)


    

    def getSalesByWeek(self, asin, start, end):
        sales = self.getSalesByDay(asin, start, end)
        sales['Week'] = sales.apply(lambda row: date.fromisoformat(row.Date).strftime('%W'), axis=1)
        sales['Month'] = sales.apply(lambda row: date.fromisoformat(row.Date).strftime('%b'), axis=1)
        return sales






    def getSalesFromAmz(self, asin, start, end, gran):
        try:
            service = AmzService()
            df = service.getSales(asin, start, end, gran)
        except: 
            service.refreshAccessToken()
            df = service.getSales(asin, start, end, gran)
        return df