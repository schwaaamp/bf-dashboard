from datetime import date, timedelta
import time
import pandas as pd
from amzService import AmzService

# Test getting financial events for yesterday
# this might be useful for figuring out what i made yesterday
service = AmzService()



#net proceeds = total balance - account level reserve - expenses - refunds
# find financial event groupid for open processingstatus and original total.currecycode = usd, currencyamount (total balance)

print("Trying to get inventory...")

df = service.getInventory()
print('Inventory...')
print(df)