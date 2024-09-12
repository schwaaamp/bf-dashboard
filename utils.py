from asinSkuUtil import asinSkuMapper

class utils:

    def getAsinListFromMapper(self):
        skus = []
        for k, v in asinSkuMapper.items():
            print(k + ' ' + str(v))
            skus.append(v[0])
        print(str(skus))
        return ''
    
    def getSkuForAsin(self, asin):
        sku = asinSkuMapper.get(asin)[0]
        return sku
    
    # I think this will only be needed for test cases
    def getAsinForSku(self, sku):
        asin = list(asinSkuMapper.keys())[list(asinSkuMapper.values()).index(sku)]
        return asin