from datetime import date, timedelta
from SPAPI_Services.amzService import AmzService

# Test getting financial events for yesterday
service = AmzService()
start = date.today() - timedelta(days=1)
end = start
df = service.getFinancialEvents(start, end)

revenue = 0.0
expenses = 0.0
eventList = df['FinancialEvents.ShipmentEventList'].values[0:1]

for orderList in eventList:
    for order in orderList:
        shipmentItemList = order['ShipmentItemList']
        for shipment in shipmentItemList:
            itemChargeList = shipment['ItemChargeList']
            for itemCharge in itemChargeList:
                amt = itemCharge['ChargeAmount']['CurrencyAmount']
                revenue += amt
                print(amt)

            itemFeesList = shipment['ItemFeeList']
            for itemFee in itemFeesList:
                fee = itemFee['FeeAmount']['CurrencyAmount']
                expenses += fee
                print(fee)

            promotionList = shipment['PromotionList']
            for promotion in promotionList:
                promotion = promotion['PromotionAmount']['CurrencyAmount']
                expenses += promotion
                print(promotion)


            try:
                itemTaxes = shipment['ItemTaxWithheldList']
                for itemTax in itemTaxes:
                    tax = itemTaxes['TaxesWithheld']['CurrencyAmount']
                    expenses += tax
                    print(tax)
            except:
                print('This order is missing the ItemTaxWithheldList')


                # https://advertising.amazon.com/about-api


print('Yesterday\'s revenue= ' + str(revenue))
print('Yesterday\'s expenses= ' + str(expenses))
print('Psuedo profit= ' + str(revenue+expenses))
# Goal is to use this to find out revenue and expenses from yesterday's transactions
# In order to fully calculate profit for yesterday, need to include expenses for inbound, storage, ppc, RATER, unit costs, etc.
# ProductAdsPaymentEvent
# Promotion
# RefundEventList
# https://developer-docs.amazon.com/sp-api/docs/finances-api-v0-model