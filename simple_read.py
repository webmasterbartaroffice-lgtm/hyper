import pandas as pd

df = pd.read_excel('new.xlsx')
print("\nColumns:")
print(df.columns.tolist())
print("\nFirst Row:")
print(df.iloc[0].to_dict())