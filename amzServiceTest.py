import datetime as date
import json
import pandas as pd
from amzService import AmzService
from utils import utils


service = AmzService()
u = utils()

# Test passing dates
print('Testing all parameters =============')
asin = u.getAsinForSku('HF-7YRO-FNSJ')
sales = service.getSales(asin, '2024-08-14', '2024-08-21', 'Day')
assert len(sales.index) == 8



# Get sales for one product for 1 week and compare to 8 week sale average
print('Testing sales for 1 product for last week and compare to 8 week average =============')
start = str(date.date.today() - date.timedelta(weeks=1)).split(' ')[0] # get start date of last week
end = start #because amz returns the whole week when passing in week granularity
start8weeksAgo = str(date.datetime.strptime(start, "%Y-%m-%d")-date.timedelta(weeks=8)).split(' ')[0] #9 bc we are comparing to last week
end8weeksAgo = str(date.datetime.fromisoformat(end) - date.timedelta(weeks=1)).split(' ')[0] #because we want all 9 weeks up to last week (total of 8 weeks of data)

sales = service.getSales(asin, start, end, 'Week')
sales8weeks = service.getSales(asin, start8weeksAgo, end8weeksAgo, 'Week')

sales.columns = ['Day', 'Unit Count', 'Order Item Count', 'Order Count', 'Avg Unit Price', 'Currency', 'Total Sales', 'Currency2']
print(sales)
sales8weeks.columns = ['Day', 'Unit Count', 'Order Item Count', 'Order Count', 'Avg Unit Price', 'Currency', 'Total Sales', 'Currency2']
avg = sales8weeks.loc[:, 'Total Sales'].mean()
print(sales8weeks)
print(avg)
assert len(sales.index) == 1
assert len(sales8weeks.index) == 8