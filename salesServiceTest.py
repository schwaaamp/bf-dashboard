import pandas as pd
from salesService import SalesService
from datetime import date, timedelta
from utils import utils
from asinSkuUtil import asinSkuMapper
from asinNameUtil import asinNames


salesService = SalesService()
utils = utils()

# Get sales for record in file
# 2023-01-14	8	8	199.92
print('Testing sales for single record in file =============')
start = date.fromisoformat('2023-01-14')
end = date.fromisoformat('2023-01-14')
asin = utils.getAsinForSku('HF-7YRO-FNSJ')
df = salesService.getSalesByDay(asin, start, end)
d = df['Date'].values[0:1][0]
unitCount = df['Unit Count'].values[0]
orderCount = df['Order Count'].values[0]
sales = df['Sales'].values[0]
assert(len(df) == 1)
assert(d == '2023-01-14')
assert(unitCount == 8)
assert(orderCount == 8)
assert(sales == 199.92)
print('PASS')



# Get sales for one asin for multiple dates
print('Testing sales for multiple records in file =============')
start = date.fromisoformat('2024-01-01')
end = date.fromisoformat('2024-01-31')
asin = utils.getAsinForSku('HF-7YRO-FNSJ')
df = salesService.getSalesByDay(asin, start, end)
assert(len(df) == 31)
print('PASS')




# Get sales for multiple asins
print('Testing sales for multiple ASINs and records in file =============')
start = date.fromisoformat('2024-08-14')
end = date.fromisoformat('2024-08-16')
results = pd.DataFrame()
for asin in asinSkuMapper.keys():
    df = salesService.getSalesByDay(asin, start, end)
    df['ASIN'] = asin
    df['Product'] = asinNames.get(asin)
    results = pd.concat([results, df])

assert(len(asinSkuMapper)*3 == 21)

asin = utils.getAsinForSku('HF-7YRO-FNSJ')
hf1 = results.query("ASIN == '" + asin + "' and Date == '2024-08-16'")
assert(hf1['Unit Count'].values[0] == 6)
assert(hf1['Order Count'].values[0] == 6)
assert(hf1['Sales'].values[0] == 149.94)

asin2 = utils.getAsinForSku('GZ-5U-PER')
g1 = results.query("ASIN == '" + asin2 + "'  and Date == '2024-08-15'")
assert(g1['Unit Count'].values[0] == 2)
assert(g1['Order Count'].values[0] == 2)
assert(g1['Sales'].values[0] == 49.98)
print('PASS')





#Get sales by week
print('Testing sales by week =============')
start = date.fromisoformat('2024-06-01')
end = date.fromisoformat('2024-08-16')
results = pd.DataFrame()
for asin in asinSkuMapper.keys():
    df = salesService.getSalesByWeek(asin, start, end)
    df['ASIN'] = asin
    df['Product'] = asinNames.get(asin)
    results = pd.concat([results, df])
#need to actually check output with assert
week_avg = results.groupby(['Week', 'ASIN'], observed=True)['Sales'].sum().reset_index()
week = date(2024, 6, 3).isocalendar().week
asin = utils.getAsinForSku('HF-10U-PER')
df = week_avg.loc[(week_avg['ASIN'].str.startswith(asin) & (week_avg['Week'] == str(week)))]
assert(679.83 == df['Sales'].values)
print('PASS')




# Get sales by week for date range starting before product launched
print('Testing sales by week for date range before product launched =============')
start = date.fromisoformat('2024-05-01')
end = date.fromisoformat('2024-08-16')
asin = utils.getAsinForSku('GZ-5U-PER')
df = salesService.getSalesByWeek(asin, start, end)
week_avg = df.groupby(['Week'], observed=True)['Sales'].sum().reset_index()
week = date(2024, 5, 16).isocalendar().week
assert(week not in week_avg)
print('PASS')