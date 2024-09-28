from datetime import date, timedelta
import time
import pandas as pd
from amzService import AmzService

# Test getting financial events for yesterday
# this might be useful for figuring out what i made yesterday
service = AmzService()
'''
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

            try:
                promotionList = shipment['PromotionList']
                for promotion in promotionList:
                    promotion = promotion['PromotionAmount']['CurrencyAmount']
                    expenses += promotion
                    print(promotion)
            except:
                print('This order is missing the promotion list')


            # I don't think I need to add this tax because we never added it from the itemCharge section
            try:
                itemTaxes = shipment['ItemTaxWithheldList']
                for itemTax in itemTaxes:
                    tax = itemTaxes['TaxesWithheld']['CurrencyAmount']
                    #expenses += tax
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
'''



def getNextToken(detailedDf, orders):
    # Check if nexttoken exists and if so make another call to get next 100 orders https://github.com/amzn/selling-partner-api-models/issues/2100
    nextToken =  detailedDf.get('NextToken')
    if nextToken is not None:
        nextToken = nextToken.values[0:1][0]
    while nextToken:
        print('getting the next token response...')
        detailedDf = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, financialEventGroupId, nextToken)
        orders = pd.concat([orders, detailedDf])
        nextToken = detailedDf.get('NextToken')
        if nextToken is not None:
            nextToken = nextToken.values[0:1][0]
    return orders



#net proceeds = total balance - account level reserve - expenses - refunds
# find financial event groupid for open processingstatus and original total.currecycode = usd, currencyamount (total balance)

print("Trying to get open payments...")
print('Getting payments from: ' + str(date.today() - timedelta(days=14)))
'''
df = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, None, None)

financialEventGroupIds = []
eventGroups = df.values[0:1][0][0:1][0]
for eventGroup in eventGroups:
    status = eventGroup['ProcessingStatus']
    if(status == 'Open'):
        financialEventGroupIds.append(eventGroup['FinancialEventGroupId'])
        originalCurrency = eventGroup['OriginalTotal']['CurrencyCode']
        if(originalCurrency == 'USD'):
            print('FinancialEventGroupId ' + eventGroup['FinancialEventGroupId'] + ' is the primary id (USD)')

# Call getFinancialEventsForGroupId to get order detail for each FinancialEventGroupId 

#results = pd.DataFrame(columns=['FinancialEventGroupId', 'CurrencyCode', 'TotalAmount'])
results = pd.DataFrame()
for financialEventGroupId in financialEventGroupIds:
    orders = pd.DataFrame()
    detailedDf = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, financialEventGroupId, None)
    eventList = detailedDf['FinancialEvents.ShipmentEventList'].values[0:1]
    something = detailedDf.values[0:1][0]
    print('eventList: ' + str(eventList))
    print('something: ' + str(something))
    orders = pd.concat([orders, detailedDf])
    # try to see if it has a nexttoken
    
    orders = getNextToken(detailedDf, orders)
    #print(detailedDf)
    results = pd.concat([results, orders])
    time.sleep(.5)

print(results)        
'''

df = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, None, None)
financialEventGroupIds = []
eventGroups = df.values[0:1][0][0:1][0]

# for eventgroupid
for eventGroup in eventGroups:
    status = eventGroup['ProcessingStatus']
    if(status == 'Open'):
        financialEventGroupId = eventGroup['FinancialEventGroupId']
        #financialEventGroupIds.append(financialEventGroupId)
        originalCurrency = eventGroup['OriginalTotal']['CurrencyCode']
        # get the total balance
        totalBalance = eventGroup['OriginalTotal']['CurrencyAmount']
        
        # get event group detail by eventgroupid
        orders = pd.DataFrame()
        
        detailedDf = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, financialEventGroupId, None)
        orders = pd.concat([orders, detailedDf])
        
        # if it has a nexttoken, retrieve those results as well
        orders = getNextToken(detailedDf, orders)
        time.sleep(.5)
        
        # Does not appear I'm getting all the order for this fincnailGroupId based on the transaction statment: https://sellercentral.amazon.com/payments/event/view?accountType=PAYABLE&groupId=JmanRVvU6lUaEbAWQ5Cumkur86O2w_TpuPMr5x30vmY&transactionstatus=RELEASED&category=DEFAULT&resultsPerPage=10&pageNumber=1
        # Transaction statement says I have 178 line items including order fees, inbound fees, refunds, reimbursements, advertising
        # Need to export the statement to figure out how to do the math and double check my work
        if(financialEventGroupId == 'JmanRVvU6lUaEbAWQ5Cumkur86O2w_TpuPMr5x30vmY')
            for o in orders.values:
            
                # add up all the reserve, expenses, loan repayments, advertisements, and refunds as expenses from orders
                expenses = 0.0
                #eventList = o['FinancialEvents.ShipmentEventList']
                #print(eventList)
                
                #for orderList in eventList:
                for orderList in o:
                    orderCount = 0
                    for order in orderList:
                        orderCount += 1
                        orderExpenses = 0.0
                        shipmentItemList = order['ShipmentItemList']
                        for shipment in shipmentItemList:
                            itemChargeList = shipment['ItemChargeList']
                            for itemCharge in itemChargeList:
                                amt = itemCharge['ChargeAmount']['CurrencyAmount']
                                #revenue += amt

                            itemFeesList = shipment['ItemFeeList']
                            for itemFee in itemFeesList:
                                fee = itemFee['FeeAmount']['CurrencyAmount']
                                expenses += fee
                                orderExpenses += fee

                            try:
                                promotionList = shipment['PromotionList']
                                for promotion in promotionList:
                                    promotion = promotion['PromotionAmount']['CurrencyAmount']
                                    expenses += promotion
                                    orderExpenses += promotion
                            except:
                                print('This order is missing the promotion list')


                            # I don't think I need to add this tax because we never added it from the itemCharge section
                            try:
                                itemTaxes = shipment['ItemTaxWithheldList']
                                for itemTax in itemTaxes:
                                    tax = itemTaxes['TaxesWithheld']['CurrencyAmount']
                                    #expenses += tax
                            except:
                                print('This order is missing the ItemTaxWithheldList')
                        
                        print('order expenses: ' + str(orderExpenses))
                    print('total orders: ' + str(orderCount))
                
                try:
                    ppcExpenses = orders['ProductAdsPaymentEventList']
                    transactionValue = ppcExpenses['TransactionValue']['CurrencyAmount']
                    expenses += transactionValue
                except:
                    print('No PPC expenses in this Financial Event Group')
                    
                try:
                    inboundFeesList = orders['ServiceFeeEventList']
                    for inboundFee in inboundFeesList:
                        fee = inboundFee['FeeList']['FeeAmount']['CurrencyAmount']
                        expenses += fee
                except:
                    print('No Inbound Fees in this Financial Event Group')
                
                
                #AdjustmentItemList
                    
                print('==========')
                print('financialEventGroupId: ' + financialEventGroupId)
                print('original currency: ' + originalCurrency)
                print('total balance: ' + str(totalBalance))
                print('expenses: ' + str(expenses))
                print('net: ' + str(totalBalance - expenses))
        

    
    
        
# subtract the expenses from the total balance
# create dataframe for results
    # eventgroupid, FinancialEventGroupStart (end += 14 days), originaltotal.currencycode, originaltotal.currencyamount (total balance), expenses, net proceeds (total balance - expenses)