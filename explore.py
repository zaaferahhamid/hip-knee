from pathlib import Path # loads a tool for working with file locations
import pandas as pd

# show every column and wide rows instead of cutting them off with "..."
pd.set_option("display.max_columns", None) # display settings only, otherwise pandas would hide the middle col
pd.set_option("display.width", 200)

data_folder = Path("data")

for csv_file in sorted(data_folder.glob("*.csv")): # finds every file ending in .csv and sorts, "csv_file in" repeats to check both files
    print("=" * 70)
    print("FILE:" , csv_file.name)

    df = pd.read_csv(csv_file) # loads file into a DataFrame (table that can worked with in code)

    print("Rows and columns:", df.shape) # shape gives the num or rows and cols - how big data is

    print("\nColumn names:")
    for name in df.columns: # prints each col on its own line 
        print("  -", name)

    print("\nFirst 5 rows:")
    print(df.head()) # shows first 5 rows 

    print("\nMissing values per column:")
    print(df.isna().sum()) # counts empty cells in each col

