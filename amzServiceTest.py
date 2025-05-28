from sp_api.api import Orders
from sp_api.base import Marketplaces
from dotenv import load_dotenv
import os
from amzService2 import getSales, getFinancialEventGroups, getInventory, getCatalogItems, getPricing

load_dotenv()

print(os.getenv("SP_API_REFRESH_TOKEN"))
print(os.getenv("LWA_APP_ID"))
print(os.getenv("LWA_CLIENT_SECRET"))

asin = 'B0D7KWQSR2'
start = '2025-05-01'
end = '2025-05-10'
granularity = 'Day'

#orders = Orders(marketplace=Marketplaces.US)

response = getSales(asin, start, end, granularity)
print('success?')
print(response)
#res = orders.get_orders(CreatedAfter='2024-01-01T00:00:00Z')
#print(res.payload)



print("================ getting financial event groups ==================")
r2= getFinancialEventGroups('2025-05-01', '', '', '')
print(r2)

print("================ getting inventory ==================")
inv = getInventory()
print(inv)


print("================ getting catalog items ==================")
cat = getCatalogItems('dust')
print(cat)



print("================ getting pricing ==================")
price = getPricing(['B0D7KWQSR2'])
print(price)