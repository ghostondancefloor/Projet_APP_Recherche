import os
import pandas as pd

directory = 'google scholar/data'


df_list = []

for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory, filename)
        df = pd.read_csv(file_path)
        df_list.append(df)

merged_df = pd.concat(df_list, ignore_index=True)

merged_df.to_csv('google scholar/data.csv', index=False)

print("CSV files merged successfully into 'merged_file.csv'")
