from config import client
from binance.enums import *
import pandas as pd
import math, csv, time
import datetime

from .function import *

def check():
    df = pd.read_csv('csv_files/token.csv')

    date = df['date']
    open = df['open']
    high = df['high']
    low = df['low']
    close = df['close']

    rsi8 = df['rsi8']
    rsi56 = df['rsi56']

    atrSA = df['atrSA']
    atrD = df['atrD']

    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)
    

    inicio = datetime.datetime.strptime(date.values[0], '%Y-%m-%d %H:%M:%S')
    month = inicio + datetime.timedelta(days=30)

    for x in range(0, rows):
        if str(month) == date.values[x]:
            add_position(x-3, "NO", 0.0, 0.0, str(date.values[x-1]), 0.0)
            break
        else:
            pass

    while True:

        # Recoger valores actuales para seguir calculando
        positionCSV = pd.read_csv('csv_files/position.csv')
        last_position = positionCSV['type'].values[-1]
        last_date = positionCSV['date'].values[-1]

        if "2022-01-20 22:00:00" <= last_date:
            break # Termina aquí el cálculo
        
        else:
            if (last_position == "NO"):
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                dateRow = position_csv['date'].values[-1]

                for n in range(lastRow+1, rows):
                    #if long
                    if ((rsi8.values[n-1] > rsi56.values[n-1]) & (rsi8.values[n-1] > 65.00)) & (open.values[n-1] < close.values[n-1]):
                        if ((rsi8.values[n] > rsi56.values[n]) & (rsi8.values[n] > 65.00)):
                            if (open.values[n] < close.values[n]) & (((close.values[n] - open.values[n])*2)>(high.values[n] - close.values[n])):
                                # Se abre LONG
                                position_long = open.values[n+1]
                                date_add = date.values[n]
                                fractal_long = open.values[n] - atrSA.values[n]

                                add_position(n, "LONG", position_long, fractal_long, date_add, 0.0)  
                                break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break                                 
                            

                    if ((rsi8.values[n-1] < rsi56.values[n-1]) & (rsi8.values[n-1] < 35.00)) & (open.values[n-1] > close.values[n]):
                        if (rsi8.values[n] < rsi56.values[n]) & (rsi8.values[n] < 35.00):#Opción de reapertura
                            if (open.values[n] > close.values[n]) & (((open.values[n] - close.values[n])*2) > (close.values[n]-low.values[n])):
                                # Se abre SHORT
                                position_short = open.values[n+1]
                                date_add = date.values[n]
                                fractal_short = open.values[n] + atrSA.values[n]

                                add_position(n, "SHORT", position_short, fractal_short, date_add,0.0)
                                break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break
                
                    #No oportunidad de abrir
                    else:
                        date_add = date.values[n]
                        add_position(n, "NO", 0.0,0.0,date_add,0.0)
                        break

            if last_position == "LONG":
                # Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_long = float(position_csv['position'].values[-1])
                fractal_long = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]

                
                for x in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_long = float(positions['sl'].values[-1])

                    if fractal_long > low.values[x]:
                        #Cerramos long
                        date_pos = date.values[x]

                        add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                        break

                    if ((close.values[x]*100)/position_long) > 101.0:
                        new_sl = round((((close.values[x] - position_long)*0.85)+position_long),4)
                        if new_sl > fractal_long:
                            change_sl(new_sl)
                            
                        else:
                            pass

                    if rsi8.values[x] < 35.00:
                        if fractal_long < close.values[x]:
                            change_sl(close.values[x])

                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                        else:
                                #Cerramos long
                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                    else:
                        pass
                        

            if last_position == "SHORT":
                #Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_short = float(position_csv['position'].values[-1])
                fractal_short = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]


                for i in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_short = float(positions['sl'].values[-1])

                    if fractal_short < high.values[i]:
                        date_pos = date.values[i]

                        add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                        break

                    if ((close.values[i]*100)/position_short) < 99.0:
                        new_sl = round(position_short - ((position_short-close.values[i])*0.85), 4)
                        if new_sl < fractal_short:
                            change_sl(new_sl)

                        else:
                            pass

                    if rsi8.values[i] > 65.00:
                        if fractal_short > close.values[i]:
                            change_sl(close.values[i])
                    
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break

                        else:
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break
                    else:
                        pass
                    

def check2():
    df = pd.read_csv('csv_files/token.csv')

    date = df['date']
    open = df['open']
    high = df['high']
    low = df['low']
    close = df['close']

    rsi8 = df['rsi8']
    rsi56 = df['rsi56']

    ema10 = df['ema10']
    ema20 = df['ema20']
    ema40 = df['ema40']

    atrSA = df['atrSA']
    atrD = df['atrD']

    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)
    

    inicio = datetime.datetime.strptime(date.values[0], '%Y-%m-%d %H:%M:%S')
    month = inicio + datetime.timedelta(days=30)

    for x in range(0, rows):
        if str(month) == date.values[x]:
            add_position(x-3, "NO", 0.0, 0.0, str(date.values[x-1]), 0.0)
            break
        else:
            pass

    while True:

        # Recoger valores actuales para seguir calculando
        positionCSV = pd.read_csv('csv_files/position.csv')
        last_position = positionCSV['type'].values[-1]
        last_date = positionCSV['date'].values[-1]

        if "2022-01-20 22:00:00" <= last_date:
            break # Termina aquí el cálculo
        
        else:
            if (last_position == "NO"):
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                dateRow = position_csv['date'].values[-1]

                for n in range(lastRow+1, rows):
                    #if long
                    if (ema10.values[n] > ema20.values[n]) & (ema20.values[n] > ema40.values[n]):
                        if ((rsi8.values[n] > rsi56.values[n]) & (rsi8.values[n] > 65.00)):
                            if (open.values[n] < close.values[n]) & (((close.values[n] - open.values[n])*2)>(high.values[n] - close.values[n])):
                                # Se abre LONG
                                position_long = open.values[n+1]
                                date_add = date.values[n]
                                fractal_long = open.values[n] - atrSA.values[n]

                                add_position(n, "LONG", position_long, fractal_long, date_add, 0.0)  
                                break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break                                 
                            

                    if (ema10.values[n] < ema20.values[n]) & (ema20.values[n] < ema40.values[n]):
                        if (rsi8.values[n] < rsi56.values[n]) & (rsi8.values[n] < 35.00):#Opción de reapertura
                            if (open.values[n] > close.values[n]) & (((open.values[n] - close.values[n])*2) > (close.values[n]-low.values[n])):
                                # Se abre SHORT
                                position_short = open.values[n+1]
                                date_add = date.values[n]
                                fractal_short = open.values[n] + atrSA.values[n]

                                add_position(n, "SHORT", position_short, fractal_short, date_add,0.0)
                                break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break
                
                    #No oportunidad de abrir
                    else:
                        date_add = date.values[n]
                        add_position(n, "NO", 0.0,0.0,date_add,0.0)
                        break

            if last_position == "LONG":
                # Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_long = float(position_csv['position'].values[-1])
                fractal_long = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]

                
                for x in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_long = float(positions['sl'].values[-1])

                    if fractal_long > low.values[x]:
                        #Cerramos long
                        date_pos = date.values[x]

                        add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                        break

                    if ((close.values[x]*100)/position_long) > 101.0:
                        new_sl = round((((close.values[x] - position_long)*0.85)+position_long),4)
                        if new_sl > fractal_long:
                            change_sl(new_sl)
                            
                        else:
                            pass

                    if rsi8.values[x] < 35.00:
                        if fractal_long < close.values[x]:
                            change_sl(close.values[x])

                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                        else:
                                #Cerramos long
                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                    else:
                        pass
                        

            if last_position == "SHORT":
                #Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_short = float(position_csv['position'].values[-1])
                fractal_short = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]


                for i in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_short = float(positions['sl'].values[-1])

                    if fractal_short < high.values[i]:
                        date_pos = date.values[i]

                        add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                        break

                    if ((close.values[i]*100)/position_short) < 99.0:
                        new_sl = round(position_short - ((position_short-close.values[i])*0.85), 4)
                        if new_sl < fractal_short:
                            change_sl(new_sl)

                        else:
                            pass

                    if rsi8.values[i] > 65.00:
                        if fractal_short > close.values[i]:
                            change_sl(close.values[i])
                    
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break

                        else:
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break
                    else:
                        pass


def check3():
    df = pd.read_csv('csv_files/token.csv')

    date = df['date']
    open = df['open']
    high = df['high']
    low = df['low']
    close = df['close']

    rsi8 = df['rsi8']
    rsi56 = df['rsi56']

    atrSA = df['atrSA']
    atrD = df['atrD']

    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)
    

    inicio = datetime.datetime.strptime(date.values[0], '%Y-%m-%d %H:%M:%S')
    month = inicio + datetime.timedelta(days=30)

    for x in range(0, rows):
        if str(month) == date.values[x]:
            add_position(x-3, "NO", 0.0, 0.0, str(date.values[x-1]), 0.0)
            break
        else:
            pass

    while True:

        # Recoger valores actuales para seguir calculando
        positionCSV = pd.read_csv('csv_files/position.csv')
        last_position = positionCSV['type'].values[-1]
        last_date = positionCSV['date'].values[-1]

        if "2022-01-20 22:00:00" <= last_date:
            break # Termina aquí el cálculo
        
        else:
            if (last_position == "NO"):
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                dateRow = position_csv['date'].values[-1]

                for n in range(lastRow+1, rows):
                    #if long
                    if ((rsi8.values[n-1] > rsi56.values[n-1]) & (rsi8.values[n-1] > 65.00)) :
                        if ((rsi8.values[n] > rsi56.values[n]) & (rsi8.values[n] > 65.00) & (open.values[n-1] < close.values[n-1])):
                            if (open.values[n] < close.values[n]) & (((close.values[n] - open.values[n])*2)>(high.values[n] - close.values[n])):
                                # Se abre LONG
                                last_pos = pd.read_csv('csv_files/last_pos.csv')
                                type_last_pos = last_pos['position'].values[-1]

                                if type_last_pos == "long":
                                    date_add = date.values[n]
                                    add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                    break

                                else:
                                    position_long = open.values[n+1]
                                    date_add = date.values[n]
                                    fractal_long = open.values[n] - atrSA.values[n]

                                    add_position(n, "LONG", position_long, fractal_long, date_add, 0.0)
                                    posicion_change("long")
                                    break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break                                 
                            

                    if ((rsi8.values[n-1] < rsi56.values[n-1]) & (rsi8.values[n-1] < 35.00)):
                        if (rsi8.values[n] < rsi56.values[n]) & (rsi8.values[n] < 35.00)  & (open.values[n-1] > close.values[n]):#Opción de reapertura
                            if (open.values[n] > close.values[n]) & (((open.values[n] - close.values[n])*2) > (close.values[n]-low.values[n])):
                                # Se abre SHORT
                                last_pos = pd.read_csv('csv_files/last_pos.csv')
                                type_last_pos = last_pos['position'].values[-1]

                                if type_last_pos == "short":
                                    date_add = date.values[n]
                                    add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                    break

                                else:
                                    position_short = open.values[n+1]
                                    date_add = date.values[n]
                                    fractal_short = open.values[n] + atrSA.values[n]

                                    add_position(n, "SHORT", position_short, fractal_short, date_add,0.0)
                                    posicion_change("short")
                                    break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break
                
                    #No oportunidad de abrir
                    else:
                        last_pos = pd.read_csv('csv_files/last_pos.csv')
                        type_last_pos = last_pos['position'].values[-1]

                        if type_last_pos == "no":
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0,0.0,date_add,0.0)
                            break
                        
                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0,0.0,date_add,0.0)
                            posicion_change("no")
                            break

            if last_position == "LONG":
                # Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_long = float(position_csv['position'].values[-1])
                fractal_long = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]

                
                for x in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_long = float(positions['sl'].values[-1])

                    if fractal_long > low.values[x]:
                        #Cerramos long
                        date_pos = date.values[x]

                        add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                        break

                    if ((close.values[x]*100)/position_long) > 101.0:
                        new_sl = round((((close.values[x] - position_long)*0.85)+position_long),4)
                        if new_sl > fractal_long:
                            change_sl(new_sl)
                            
                        else:
                            pass

                    if rsi8.values[x] < 35.00:
                        if fractal_long < close.values[x]:
                            change_sl(close.values[x])

                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                        else:
                                #Cerramos long
                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                    else:
                        pass
                        

            if last_position == "SHORT":
                #Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_short = float(position_csv['position'].values[-1])
                fractal_short = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]


                for i in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_short = float(positions['sl'].values[-1])

                    if fractal_short < high.values[i]:
                        date_pos = date.values[i]

                        add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                        break

                    if ((close.values[i]*100)/position_short) < 99.0:
                        new_sl = round(position_short - ((position_short-close.values[i])*0.85), 4)
                        if new_sl < fractal_short:
                            change_sl(new_sl)

                        else:
                            pass

                    if rsi8.values[i] > 65.00:
                        if fractal_short > close.values[i]:
                            change_sl(close.values[i])
                    
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break

                        else:
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break
                    else:
                        pass


def check4():
    df = pd.read_csv('csv_files/token.csv')

    date = df['date']
    open = df['open']
    high = df['high']
    low = df['low']
    close = df['close']

    rsi8 = df['rsi8']
    rsi56 = df['rsi56']

    ema10 = df['ema10']
    ema20 = df['ema20']
    ema40 = df['ema40']

    atrSA = df['atrSA']
    atrD = df['atrD']

    index = df.index
    number_of_rows = len(index)
    rows = int(number_of_rows)
    

    inicio = datetime.datetime.strptime(date.values[0], '%Y-%m-%d %H:%M:%S')
    month = inicio + datetime.timedelta(days=30)

    for x in range(0, rows):
        if str(month) == date.values[x]:
            add_position(x-3, "NO", 0.0, 0.0, str(date.values[x-1]), 0.0)
            break
        else:
            pass

    while True:

        # Recoger valores actuales para seguir calculando
        positionCSV = pd.read_csv('csv_files/position.csv')
        last_position = positionCSV['type'].values[-1]
        last_date = positionCSV['date'].values[-1]

        if "2022-01-20 22:00:00" <= last_date:
            break # Termina aquí el cálculo
        
        else:
            if (last_position == "NO"):
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                dateRow = position_csv['date'].values[-1]

                for n in range(lastRow+1, rows):
                    #if long
                    if (ema10.values[n] > ema20.values[n]) & (ema20.values[n] > ema40.values[n]):
                        if ((rsi8.values[n-1] > rsi56.values[n-1]) & (rsi8.values[n-1] > 65.00) & (open.values[n-1] < close.values[n-1])) &((rsi8.values[n-1] > rsi56.values[n-1]) & (rsi8.values[n-1] > 65.00)):
                            if (open.values[n] < close.values[n]) & (((close.values[n] - open.values[n])*2)>(high.values[n] - close.values[n])):
                                # Se abre LONG
                                last_pos = pd.read_csv('csv_files/last_pos.csv')
                                type_last_pos = last_pos['position'].values[-1]

                                if type_last_pos == "long":
                                    date_add = date.values[n]
                                    add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                    break

                                else:
                                    position_long = open.values[n+1]
                                    date_add = date.values[n]
                                    fractal_long = open.values[n] - atrSA.values[n]

                                    add_position(n, "LONG", position_long, fractal_long, date_add, 0.0)
                                    posicion_change("long")
                                    break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break                                 
                            

                    if (ema10.values[n] < ema20.values[n]) & (ema20.values[n] < ema40.values[n]):
                        if (rsi8.values[n] < rsi56.values[n]) & (rsi8.values[n] < 35.00)  & (open.values[n-1] > close.values[n]) & ((rsi8.values[n-1] < rsi56.values[n-1]) & (rsi8.values[n-1] < 35.00)):#Opción de reapertura
                            if (open.values[n] > close.values[n]) & (((open.values[n] - close.values[n])*2) > (close.values[n]-low.values[n])):
                                # Se abre SHORT
                                last_pos = pd.read_csv('csv_files/last_pos.csv')
                                type_last_pos = last_pos['position'].values[-1]

                                if type_last_pos == "short":
                                    date_add = date.values[n]
                                    add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                    break

                                else:
                                    position_short = open.values[n+1]
                                    date_add = date.values[n]
                                    fractal_short = open.values[n] + atrSA.values[n]

                                    add_position(n, "SHORT", position_short, fractal_short, date_add,0.0)
                                    posicion_change("short")
                                    break

                            else:
                                date_add = date.values[n]
                                add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                                break

                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0, 0.0, date_add, 0.0)
                            break
                
                    #No oportunidad de abrir
                    else:
                        last_pos = pd.read_csv('csv_files/last_pos.csv')
                        type_last_pos = last_pos['position'].values[-1]

                        if type_last_pos == "no":
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0,0.0,date_add,0.0)
                            break
                        
                        else:
                            date_add = date.values[n]
                            add_position(n, "NO", 0.0,0.0,date_add,0.0)
                            posicion_change("no")
                            break

            if last_position == "LONG":
                # Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_long = float(position_csv['position'].values[-1])
                fractal_long = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]

                
                for x in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_long = float(positions['sl'].values[-1])

                    if fractal_long > low.values[x]:
                        #Cerramos long
                        date_pos = date.values[x]

                        add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                        break

                    if ((close.values[x]*100)/position_long) > 101.0:
                        new_sl = round((((close.values[x] - position_long)*0.85)+position_long),4)
                        if new_sl > fractal_long:
                            change_sl(new_sl)
                            
                        else:
                            pass

                    if rsi8.values[x] < 35.00:
                        if fractal_long < close.values[x]:
                            change_sl(close.values[x])

                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                        else:
                                #Cerramos long
                            date_pos = date.values[x]

                            add_position(x, "NO", 0.0, 0.0,date_pos,0.0)
                            break

                    else:
                        pass
                        

            if last_position == "SHORT":
                #Bucle para calcular beneficio
                position_csv = pd.read_csv('csv_files/position.csv')
                lastRow = int(position_csv['row'].values[-1])
                position_short = float(position_csv['position'].values[-1])
                fractal_short = float(position_csv['sl'].values[-1])
                date_pos = position_csv['date'].values[-1]


                for i in range(lastRow, rows):
                    positions = pd.read_csv('csv_files/position.csv')
                    fractal_short = float(positions['sl'].values[-1])

                    if fractal_short < high.values[i]:
                        date_pos = date.values[i]

                        add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                        break

                    if ((close.values[i]*100)/position_short) < 99.0:
                        new_sl = round(position_short - ((position_short-close.values[i])*0.85), 4)
                        if new_sl < fractal_short:
                            change_sl(new_sl)

                        else:
                            pass

                    if rsi8.values[i] > 65.00:
                        if fractal_short > close.values[i]:
                            change_sl(close.values[i])
                    
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break

                        else:
                            date_pos = date.values[i]

                            add_position(i, "NO", 0.0, 0.0, date_pos, 0.0)
                            break
                    else:
                        pass

            

