from datetime import date, timedelta
from amzService import AmzService

def getOpenPayments():
    amzService = AmzService()
    df = amzService.getFinancialEventGroups(date.today() - datetime.timedelta(days=14), None)
    print(df)