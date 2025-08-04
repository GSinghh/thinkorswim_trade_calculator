import pandas as pd
import re
overall_profit_loss = 0
df = pd.read_csv("trades.csv", on_bad_lines='skip' ,header=2)
df = df.drop('REF #', axis=1)
filtered_trades = df[df['TYPE'] == 'TRD']

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

all_trades = {}
#### All Combinations of Trades that can take place ####
"""
1. Single Contract (BUY -> SELL)
2. Multiple Contracts (BUY -> BUY -> SELL -> SELL)
3. Same Contract (BUY -> SELL -> BUY -> SELL)
4.  
"""

def calculate_stats(trades):
    global overall_profit_loss
    # 1. Iterate through all trades
    # 2. Categorize the trade
    """
        - While contracts are open, they all belong to the same segment
        - When the number of contracts closes, they become a seperate segment
        - Even if the the option is exactly the same 
    """
    current_segment = []
    segments = []
    open_contracts = 0
    
    for trade in trades: 
        quantity = trade['Quantity']
        cost = trade['Cost']  
        fees = trade['Fees']
        premium = trade['Premium']
        action = trade['Action']
        
        if action == "BOT":
            open_contracts += quantity
            current_segment.append(trade)
        else:
            open_contracts -= quantity
            current_segment.append(trade)
        if open_contracts == 0:
            segments.append(current_segment)
            current_segment = []
    
    for seg in segments:
        total_contracts = 0
        open_contracts = 0
        total_fees = 0.0
        total_cost_basis = 0.0
        realized_pnl = 0.0
        avg_contract_price = 0
        total_pnl = 0.0
        win_or_loss = ''
        
        for idx, trade in enumerate(seg):
            quantity = trade['Quantity']
            cost = trade['Cost']  
            fees = trade['Fees']
            premium = trade['Premium']
            action = trade['Action']
            total_fees += fees
            num_trades = len(seg) - 1
            
            if action == 'BOT':
                total_contracts += quantity
                open_contracts += quantity
                avg_contract_price = round(((avg_contract_price * (total_contracts - quantity)) + (quantity * premium)) / total_contracts, 2)
                total_cost_basis += abs(cost)
            else:
                open_contracts -= quantity
                realized_pnl += (premium - avg_contract_price) * 100
            if action != 'BOT':
                pnl = ((premium - avg_contract_price) * 100)
                total_pnl = realized_pnl - total_fees
                overall_profit_loss += total_pnl
                win_or_loss = 'W' if total_pnl > 0 else 'L'
                print(f"Date: {trade['Date']}\nTime: {trade['Time']}\nPosition: {trade['Action']} {trade['Quantity']} {key}")
                print(f"Total Contracts: {total_contracts} \nOpen Contracts: {open_contracts} \nAverage Contract Price: {avg_contract_price} \nTotal Cost Basis: {total_cost_basis}")
                print(f"Win or Loss: {win_or_loss}")
                print(f"Profit and Loss: {pnl:.2f}\n")
                if idx == num_trades: print(f"Total PnL: {total_pnl:.2f}\n") 


for idx, row in filtered_trades.iterrows():
    execution_date = row["DATE"]
    execution_time = row["TIME"]
    description = row["DESCRIPTION"]
    commission = abs(float(row["Misc Fees"])) + abs(float(row["Commissions & Fees"]))
    cost_before_conversion = row["AMOUNT"]
    cost = float(cost_before_conversion.replace(',', '') if ',' in cost_before_conversion else cost_before_conversion)
    contract_info = options_pattern.match(description) # Extract information related to option contract
    if not contract_info:
        continue 
    
    trade_info = {
        "Action": contract_info["action"],
        "Name": f"{contract_info['symbol']} {contract_info['strike']} {contract_info['right']}",
        "Expiration": f"{contract_info['day']} {contract_info['month']} {contract_info['year']}",
        "Date": execution_date,
        "Time": execution_time,
        "Cost": cost,
        "Premium": float(contract_info['premium']),
        "Quantity": abs(int(contract_info["quantity"])),
        "Exchange": contract_info["exchange"] if contract_info["exchange"] is not None else "",
        "Fees": commission,
        }
    
    key = f"{trade_info['Name']} {trade_info['Expiration']}"
    all_trades.setdefault(key, []).append(trade_info)
    

for key in all_trades:
    calculate_stats(all_trades[key])
    
print(f"Overall Profit and Loss: {overall_profit_loss:.2f}")