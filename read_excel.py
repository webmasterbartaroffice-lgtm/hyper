import pandas as pd

# Read the Excel file
df = pd.read_excel('new.xlsx')

# Display column information
print("\nColumn names and their positions:")
print("=" * 50)
for i, col in enumerate(df.columns):
    print(f"Column {i}: '{col}' (type: {type(col)})")

# Display first few rows with specific columns
print("\nFirst few rows with SKU and price columns:")
print("=" * 50)
print(df[['كد كالا', 'قيمت فروش']].head()) 