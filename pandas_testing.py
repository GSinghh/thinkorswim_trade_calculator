import pandas as pd
import re
df = pd.read_csv("trades.csv", on_bad_lines='skip' ,header=2)
df = df.drop('REF #', axis=1)
filtered_trades = df[df['TYPE'] == 'TRD']
# filtered_trades.to_csv('filtered_trades.csv')
# df = df.set_index('DATE')

options_pattern = re.compile(
    r'(?P<action>BOT|SOLD)\s+'                   # buy or sell
    r'(?P<quantity>[+-]?\d+)\s+'                 # +1, -2, etc.
    r'(?P<symbol>[A-Z]+)\s+'                     # underlying ticker
    r'(?P<multiplier>\d+)\s*'                    # usually 100
    r'(?:\((?P<series>[^)]+)\)\s+)?'             # optional (Weekly, Monthly) etc
    r'(?P<day>\d{1,2})\s+'                       # expiration day
    r'(?P<month>[A-Z]{3})\s+'                    # expiration month, e.g. MAR
    r'(?P<year>\d{2})\s+'                        # expiration year, e.g. 25
    r'(?P<strike>\d+(?:\.\d+)?)\s+'              # strike price
    r'(?P<right>CALL|PUT)\s+'                    # CALL or PUT
    r'@(?P<premium>[\d\.]+)'                      # @.29, @1.05, etc.
    r'(?:\s+(?P<exchange>[A-Z]+))?'              # Exchange Code, e.g. CBOE, NASDAQ
)


# This list will store all open trades
open_trades = []
closed_trades = []

for idx, row in filtered_trades.head(4).iterrows():
    execution_date = row["DATE"]
    execution_time = row["TIME"]
    description = row["DESCRIPTION"]
    commission = abs(float(row["Misc Fees"])) + abs(float(row["Commissions & Fees"]))
    cost = abs(float(row["AMOUNT"]))
    contract_info = options_pattern.match(description) # Extract information related to option contract name
    # contract = f"{contract_info['symbol']} {contract_info['strike']} {contract_info['right']} {contract_info['day']} {contract_info['month']} {contract_info['year']}"
    if contract_info["action"] == 'BOT':
        open_trades.append(contract_info.groupdict())
    else:
        for trade in open_trades:
            print(trade)
    
    
    
    # print(f'Index: {idx}\n', f'Row: {row}')
    # print(f'Date: {row["DATE"]}')
    # print(f'Time: {row["TIME"]}')
    # print(f'Trade: {row["DESCRIPTION"]}')
    # print(f'Fees: {row["Misc Fees"]}')
    # print(f'Commission: {row["Commissions & Fees"]}')
    # print(f'Cost: {row["AMOUNT"]}\n')
    
    

# extracted_data = df['DESCRIPTION'].str.extract(pattern)
# extracted_data = extracted_data.set_index('DATE')
# extracted_data.to_csv('test_data.csv')
# print(extracted_data)