from PreProcess import ceo_data
import json,pandas as pd

data=json.load(open("test.json","r")) ## input files

result=ceo_data(data)

df=pd.DataFrame(result)
print(df.head(30))