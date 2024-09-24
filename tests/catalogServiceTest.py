from SPAPI.catalogService import CatalogService

service = CatalogService()
df = service.getSearchResults()
print(df)

print(df.loc[df.isin(['Buckeye Farms']).any(axis=1)].index.tolist())