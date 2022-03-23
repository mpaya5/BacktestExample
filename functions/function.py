import csv, math
import pandas as pd
import pandas_ta as pta
import numpy as np
import talib as ta
from config import client



def data_log_to_file(message):
    with open('csv_files/symbol.txt', 'a+') as f:
        f.write(message)

def data_log_file(message, symbol):
    with open(f'csv_files/{symbol}.txt', 'a+') as f:
        f.write(message)

        
def start(symbol, number):
    # PRimero calcular los candlesticks
    df = pd.DataFrame(client.futures_historical_klines(symbol=symbol, interval="1h", start_str="2020-6-10", end_str=None))

    # crop unnecessary columns
    df = df.iloc[:, :6]
    # ascribe names to columns
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    # convert timestamp to date format and ensure ohlcv are all numeric
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col])
    df.head()

    #EMAS
    EMA10 = df.close.ewm(span=4, adjust=False).mean()
    df['ema10'] = round(EMA10, number)
    EMA20 = df.close.ewm(span=9, adjust=False).mean()
    df['ema20'] = round(EMA20, number)
    EMA40 = df.close.ewm(span=18, adjust=False).mean()
    df['ema40'] = round(EMA40, number)

    #RSI y RSI-based-MA
    rsiLengthInput = 8
    rsiSourceInput = df['close']
    maLengthInput = 56
    bbMultInput = 2
    rsiMA = ta.RSI(rsiSourceInput, timeperiod=rsiLengthInput)
    df['rsi8'] = round(rsiMA, number)
    ma = ta.EMA(rsiMA, 56)
    df['rsi56'] = round(ma, number)
    
    #ATR SL
    ATRlen = 14
    ATRsrc = df['open']

    atr = ta.TRANGE(df['high'], df['low'], df['close'])
    stop_atr = pta.rma(atr, ATRlen)
    df['atrSA'] = round(stop_atr, number)
    direction = pta.rma(ATRsrc, ATRlen)
    df['atrD'] = round(direction, number)

    # if df['open'].values[-1] > direction:
    #     ATRsl = df['open'].values[-1] - stop_atr
    #     df['ATRsl'] = round(ATRsl, number)
    # else:
    #     ATRsl = df['open'].values[-1] + stop_atr
    #     df['ATRsl'] = round(ATRsl, number)

    n=1
    df = df.head(-n)

    df.to_csv('csv_files/token.csv', index=False, encoding='utf-8')




def add_position(row,type,position,sl,date,balance):
    myData = [row,type,position,sl,date,balance]
    myFile = open('csv_files/position.csv', 'a+')
    writer = csv.writer(myFile)
    writer.writerow(myData)
    myFile.close()


def change_sl(sl):
    df = pd.read_csv('csv_files/position.csv')
    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)
    df.loc[rows-1, 'sl'] = sl
    df.to_csv('csv_files/position.csv', index=False)


def delete_total():
    df = pd.read_csv('csv_files/position.csv')

    index = df.index
    number = len(index)
    rows = int(number)

    df = df.head(-rows)
    df.to_csv('csv_files/position.csv', index=False, encoding='utf-8')

    dfbal = pd.read_csv('csv_files/position.csv')
    indice = dfbal.index
    numero = len(indice)
    lineas = int(numero)

    dfbal = dfbal.head(-lineas)
    dfbal.to_csv('csv_files/balance.csv', index=False, encoding='UTF-8')



def balance_calc():
    df = pd.read_csv('csv_files/position.csv')
    type = df['type']
    entryPoint = df['position']
    sl = df['sl']

    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)

    for i in range(1,rows):
        position = entryPoint.values[i]
        stop_loss = sl.values[i]

        if type.values[i] == "LONG":
            beneficio = (100-(position*100/stop_loss))
            if beneficio < -10.00:
                beneficio = -10.00
                df.loc[i, 'balance'] = beneficio
                df.to_csv('csv_files/position.csv', index=False)
            
            else:

                df.loc[i, 'balance'] = beneficio
                df.to_csv('csv_files/position.csv', index=False)

        if type.values[i] == "SHORT":
            beneficio = ((position*100/stop_loss)-100)

            if beneficio < -10.00:
                beneficio = -10.00
                df.loc[i, 'balance'] = beneficio
                df.to_csv('csv_files/position.csv', index=False)
            
            else:

                df.loc[i, 'balance'] = beneficio
                df.to_csv('csv_files/position.csv', index=False)
        if type.values[i] == "NO":
            pass

    new_balance = 0.0
    x = 1
    myData = [new_balance, x]
    myFile = open('csv_files/balance.csv', 'a+')
    writer = csv.writer(myFile)
    writer.writerow(myData)
    myFile.close()

    df = pd.read_csv('csv_files/position.csv')
    datet_df = df['date']
    entryPoint = df['position']
    balance = df['balance']
    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)


    for x in range(1, rows):
        balancex = float(balance.values[x])
        if balancex == 0:
            pass
        else:
            balance_df = pd.read_csv('csv_files/balance.csv')
            last_balance = float(balance_df['balance'].values[-1])
            new_balance = last_balance + balancex

            myData = [new_balance, x]
            myFile = open('csv_files/balance.csv', 'a+')
            writer = csv.writer(myFile)
            writer.writerow(myData)
            myFile.close()


def posicion_change(pos):
    df = pd.read_csv('csv_files/last_pos.csv')
    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)
    df.loc[rows-1, 'position'] = pos
    df.to_csv('csv_files/last_pos.csv', index=False)    
