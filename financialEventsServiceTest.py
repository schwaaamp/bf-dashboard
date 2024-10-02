from datetime import date, timedelta
import time
import pandas as pd
from amzService import AmzService

# Test getting financial events for yesterday
# this might be useful for figuring out what i made yesterday
service = AmzService()

# https://advertising.amazon.com/about-api

# Goal is to use this to find out revenue and expenses from yesterday's transactions
# In order to fully calculate profit for yesterday, need to include expenses for inbound, storage, ppc, RATER, unit costs, etc.
# ProductAdsPaymentEvent
# Promotion
# RefundEventList
# https://developer-docs.amazon.com/sp-api/docs/finances-api-v0-model


#def getOrdersForDataframe(df, orders_array):
def getOrdersForDataframe(df, order_array):
    for records in df.values:
        for i in range(len(records)):
            g = records[i]
            if isinstance(g, list):
                for line_item in g:
                    order_array.append(line_item)
    print('total line items: ' + str(len(order_array)))
    return order_array


def getNextToken(detailedDf, order_array):
    # Check if nexttoken exists and if so make another call to get next 100 orders https://github.com/amzn/selling-partner-api-models/issues/2100
    nextToken =  detailedDf.get('NextToken')
    if nextToken is not None:
        nextToken = nextToken.values[0:1][0]
    while nextToken:
        print('getting the next token response...')
        detailedDf = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, financialEventGroupId, nextToken)
        order_array.append(getOrdersForDataframe(detailedDf, order_array))
        nextToken = detailedDf.get('NextToken')
        if nextToken is not None:
            nextToken = nextToken.values[0:1][0]
    #return orders
    return order_array



#net proceeds = total balance - account level reserve - expenses - refunds
# find financial event groupid for open processingstatus and original total.currecycode = usd, currencyamount (total balance)

print("Trying to get open payments...")
print('Getting payments from: ' + str(date.today() - timedelta(days=14)))

df = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, None, None)
financialEventGroupIds = []
eventGroups = df.values[0:1][0][0:1][0]

result = pd.DataFrame()

# for eventgroupid
for eventGroup in eventGroups:
    eventGroupStart = eventGroup['FinancialEventGroupStart']
    status = eventGroup['ProcessingStatus']
    if(status == 'Open'):
        financialEventGroupId = eventGroup['FinancialEventGroupId']
        #financialEventGroupIds.append(financialEventGroupId)
        originalCurrency = eventGroup['OriginalTotal']['CurrencyCode']
        # get the total balance
        totalBalance = eventGroup['OriginalTotal']['CurrencyAmount']
        
        # get event group detail by eventgroupid
        order_array = []
        
        detailedDf = service.getFinancialEventGroups(date.today() - timedelta(days=14), None, financialEventGroupId, None)
        order_array = getOrdersForDataframe(detailedDf, order_array)
        
        # if it has a nexttoken, retrieve those results as well
        order_array = getNextToken(detailedDf, order_array)
        #print('financialEventGroupId: ' + financialEventGroupId)
        #print('order_array length: ' + str(len(order_array)))
        time.sleep(.5)
        
        #print(order_array)
        
        # Does not appear I'm getting all the order for this fincnailGroupId based on the transaction statment: https://sellercentral.amazon.com/payments/event/view?accountType=PAYABLE&groupId=JmanRVvU6lUaEbAWQ5Cumkur86O2w_TpuPMr5x30vmY&transactionstatus=RELEASED&category=DEFAULT&resultsPerPage=10&pageNumber=1
        # Transaction statement says I have 178 line items including order fees, inbound fees, refunds, reimbursements, advertising
        
        # add up all the reserve, expenses, loan repayments, advertisements, and refunds as expenses from orders
        expenses = 0.0
        orderExpenses = 0.0
        adjustments = 0.0
        allTheFees = dict(ORDER_FEES=0.0, TRANSPORTATION_FEES=0.0, PPC_FEES=0.0, ADJUSTMENTS=0.0, DEBT_RECOVERY=0.0)
        for order in order_array:
            
            try:
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
                        allTheFees['ORDER_FEES'] += fee

                    try:
                        promotionList = shipment['PromotionList']
                        for promotion in promotionList:
                            promotion = promotion['PromotionAmount']['CurrencyAmount']
                            expenses += promotion
                            orderExpenses += promotion
                            #print('promotion: ' + str(promotion))
                    except:
                        pass


                    # I don't think I need to add this tax because we never added it from the itemCharge section
                    '''
                    try:
                        itemTaxes = shipment['ItemTaxWithheldList']
                        for itemTax in itemTaxes:
                            tax = itemTaxes['TaxesWithheld']['CurrencyAmount']
                            #expenses += tax
                    except:
                        pass
                    '''
            except:
                pass
                                      
            #print('order expenses: ' + str(orderExpenses))
            
            try:
                adjustmentType = order['AdjustmentType']
                adjustmentAmount = order['AdjustmentAmount']['CurrencyAmount']
                adjustments += adjustmentAmount
                #print('adjustment: ' + adjustmentType + ' ' + str(adjustmentAmount))
                allTheFees['ADJUSTMENTS'] += adjustments
            except:
                pass
            
            
            # PPC 
            # Should I try to get this from the advertising API instead?
            '''
            [{
                'postedDate': '2024-09-19T19:48:59Z',
                'transactionType': 'Charge',
                'invoiceId': 'TRBYTQG3Q-87',
                'baseValue': {
                    'CurrencyCode': 'USD',
                    'CurrencyAmount': -501.79
                },
                'taxValue': {
                    'CurrencyCode': 'USD',
                    'CurrencyAmount': 0.0
                },
                'transactionValue': {
                    'CurrencyCode': 'USD',
                    'CurrencyAmount': -501.79
                }
            }]
            '''
            
            try:
                # Can I get this from the advertising API?
                ppcExpenses = order['ProductAdsPaymentEventList']
                transactionValue = ppcExpenses['TransactionValue']['CurrencyAmount']
                #print('PPC fee: ' + str(transactionValue))
                expenses += transactionValue
                allTheFees['PPC_FEES'] += transactionValue
            except:
                pass
            
            try:
                randomFees = order['FeeList']
                inboundConvenienceFee = 0.0
                for f in randomFees:
                    inboundConvenienceFee = f['FeeAmount']['CurrencyAmount']
                    expenses += inboundConvenienceFee
                #print('inboundConvenienceFee: ' + str(inboundConvenienceFee))
                allTheFees['TRANSPORTATION_FEES'] += inboundConvenienceFee
            except:
                pass
                
            try:
                inboundFeesList = order['ServiceFeeEventList']
                inboundFee = 0.0
                for inboundFee in inboundFeesList:
                    inboundFee = inboundFee['FeeList']['FeeAmount']['CurrencyAmount']
                    expenses += inboundFee
                #print('Inbound fee: ' + str(inboundFee))
                allTheFees['TRANSPORTATION_FEES'] += inboundFee
            except:
                pass
            
            try:
                # Believe this is when I owe for selling in this marketplace but haven't made any money, so I owe the selling fee
                debtRecoveryType = order['DebtRecoveryType']
                debtFee = 0.0
                for itemList in order['DebtRecoveryItemList']:
                    debtFee += itemList['OriginalAmount']['CurrencyAmount']
                expenses += debtFee
                allTheFees['DEBT_RECOVERY'] += debtFee
            except:
                pass
            
        
        tempDf = pd.DataFrame({'FinancialEventGroupId':[financialEventGroupId], 'eventGroupStart':[eventGroupStart], 'Status':[status], 'Currency':[originalCurrency], 'Total Balance':[totalBalance], 'Fees':[allTheFees]})
        #print(tempDf)
        result = pd.concat([result, tempDf])
        '''
        print('==========')
        print('financialEventGroupId: ' + financialEventGroupId)
        print('original currency: ' + originalCurrency)
        print('total balance: ' + str(totalBalance))
        print('expenses: ' + str(expenses))
        print('adjustments: ' + str(adjustments))
        print('net: ' + str(totalBalance + expenses))
        '''
print(result)

# Still need to look at promotions, they deduct for free shipping and there is a big chunk for previous reserve


#order fees: -2384.83
#other: +2877.53 (previous reserve + reimbursements)
#refunds: -57.18 ( original sale price (neg) + amazonFees(pos))
#transportation: -166.12
#ppc: -350.32 - 501.79 = -852.11 ?????
# total (minus other) = 3460.24


    
    
        
# subtract the expenses from the total balance
# create dataframe for results
    # eventgroupid, FinancialEventGroupStart (end += 14 days), originaltotal.currencycode, originaltotal.currencyamount (total balance), expenses, net proceeds (total balance - expenses)