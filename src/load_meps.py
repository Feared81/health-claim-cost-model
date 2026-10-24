import pandas as pd

df = pd.read_stata("data/raw/meps/2023/h251.dta", convert_categoricals=False)
print(df.shape)
print(df.columns[:50])
