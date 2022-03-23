from functions.maincopy import *
from functions.function import *
import pandas as pd
from config import client

# Todas los tokens
account = client.futures_account()
positions = account['positions']

for token in positions:
    symbol = token['symbol']
    if token['positionSide'] == "BOTH":
        data_log_to_file("_______________________________________\n")

        message = "SÍMBOLO: "+symbol+"\n"
        print(message)
        data_log_to_file(message)
        
        # Pick pricePrecision
        exInfo = client.futures_exchange_info()
        symbolExInfo = exInfo['symbols']
        for simbolo in symbolExInfo:
            if simbolo['symbol'] == symbol:
                number = int(simbolo['pricePrecision'])
                start(symbol, number)
                break

        # Empieza el bucle que detecta todos los tokens
        while True:
            token_csv = pd.read_csv('csv_files/token.csv')
            date = token_csv['date']
            if date.values[0] > "2020-12-10 00:00:00":
                data_log_to_file("No hay días suficientes para trabajar con este token, quizás más adelante.\n")
                break

            else:
                check_2()
                balance_calc()

                for x in range(0, 11):
                    change_balance(x)
                    df = pd.read_csv('csv_files/balances.csv')
                    month = str(df['month'].values[x])
                    balance = str(df['balance'].values[x])

                    data_log_to_file(month+": "+balance+"%\n")

                total = 0.0
                df = pd.read_csv('csv_files/balances.csv')
                balance_df = df['balance']
                
                for i in range(0,11):
                    total = total +balance_df.values[i]
                

                media = round(total/11)
                
                data_log_to_file("BALANCE TOTAL: "+ str(round(total, 3))+"%\n")
                data_log_to_file("MEDIA TOTAL: "+ str(media)+"%\n\n")

                balance_cero()
                delete_total()
                break