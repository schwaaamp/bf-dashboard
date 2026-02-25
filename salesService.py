from datetime import date, timedelta
from pathlib import Path
import pandas as pd
#from amzService import AmzService
from amzService2 import getSales
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

            existing_dates = set(f['Date'].values)
            launch_date = f['Date'].iloc[0]
            today = str(date.today())
            requested_dates = set(
                str(start + timedelta(days=i))
                for i in range(delta.days + 1)
            )

            missing_days = sorted([
                d for d in requested_dates
                if d not in existing_dates and d > launch_date
            ])

            df_new = pd.DataFrame()
            if missing_days:
                batch_start = missing_days[0]
                batch_end   = missing_days[-1]
                print(f'Fetching {len(missing_days)} missing days for {sku} ({batch_start} to {batch_end})')
                raw = self.getSalesFromAmz(asin, batch_start, batch_end, 'Day')
                df_new = pd.DataFrame({
                    "Date":        raw['interval'].str.slice(0, 10),
                    "Unit Count":  raw['unitCount'],
                    "Order Count": raw['orderCount'],
                    "Sales":       raw['totalSales.amount']
                })
                to_save = df_new[df_new['Date'] != today]
                if not to_save.empty:
                    print(f'Adding {len(to_save)} days to {sales_file}')
                    to_save.to_csv('csvs/' + sku + '.csv', sep='\t', encoding='utf-8', index=False, header=False, mode='a')

            csv_results = f[f['Date'].isin(requested_dates)]
            new_results  = df_new[df_new['Date'].isin(set(missing_days))] if not df_new.empty else pd.DataFrame()
            return pd.concat([csv_results, new_results])
        else:
            print('File does not exist')
            # Create sales.csv file
            df = self.getSalesFromAmz(asin, start, end, 'Day')
            df_clean = pd.DataFrame({"Date":df['interval'].str.slice(0,10), "Unit Count":df['unitCount'], "Order Count":df['orderCount'], "Sales":df['totalSales.amount']})
            print(df_clean)
            df_clean.to_csv('csvs/' + sku + '.csv', sep='\t', encoding='utf-8', index=False, header=True)


    

    def getSalesByWeek(self, asin, start, end):
        sales = self.getSalesByDay(asin, start, end)
        sales['Week'] = sales.apply(lambda row: date.fromisoformat(row.Date).strftime('%V'), axis=1)
        sales['Month'] = sales.apply(lambda row: date.fromisoformat(row.Date).strftime('%b'), axis=1)
        sales['Year'] = sales.apply(lambda row: date.fromisoformat(row.Date).strftime('%Y'), axis=1)
        return sales






    def getSalesFromAmz(self, asin, start, end, gran):
        #try:
        #print('Getting sales from Amazon for ' + start + ' - ' + end + ' for asin: ' + asin + ' and granularity: ' + gran + '...')
        #service = AmzService()
        df = getSales(asin, start, end, gran)
        #except: 
        #    service.refreshAccessToken()
        #    df = service.getSales(asin, start, end, gran)
        return df