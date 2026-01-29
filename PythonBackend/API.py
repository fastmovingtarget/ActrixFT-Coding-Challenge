import sqlite3, csv, os, numpy as np
from flask import Flask, request
from scipy.optimize import curve_fit
from datetime import datetime

app = Flask(__name__)

def initialise_db():
    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    res = cursor.execute(f'SELECT name FROM sqlite_master')
    if res.fetchone() is not None:
        print("Database already initialised")
        return

    cursor.execute("CREATE TABLE IF NOT EXISTS yields (Date TEXT, Country TEXT, Instrument TEXT, Maturity REAL, Yield REAL)")

    for file in os.listdir('./Data'):
        print(f'Reading File: {file}')
        with open(f'./Data/{file}', 'r') as fileData:
            dr = csv.DictReader(fileData, fieldnames=['Date', 'Yield'])
            to_db = []
            country = 0
            instrument = ""
            maturity = 0.0
            for i in dr:
                # if any of the constants haven't been populated for this csv
                if country == "" or instrument == "" or maturity == 0.0:
                    print(f'Yield: {i['Yield']}')
                    # populate them from the given values in the first row
                    if 'DGS' in i['Yield']:
                        country = 'US'
                        instrument = 'Treasury'
                        if '1MO' in i['Yield']:
                            maturity = 1/12
                        elif '3MO' in i['Yield']:
                            maturity = 0.25
                        elif '6MO' in i['Yield']:
                            maturity = 0.5
                        elif '10' in i['Yield']:
                            maturity = 10
                        elif '20' in i['Yield']:
                            maturity = 20
                        elif '30' in i['Yield']:
                            maturity = 30
                        elif '1' in i['Yield']:
                            maturity = 1
                        elif '2' in i['Yield']:
                            maturity = 2
                        elif '5' in i['Yield']:
                            maturity = 5
                    if 'British' in i['Yield']:
                        country = 'UK'
                        instrument = 'Gilt'
                        if '5' in i['Yield']:
                            maturity = 5
                        elif '10' in i['Yield']:
                            maturity = 10
                        elif '20' in i['Yield']:
                            maturity = 20
                        
                    print(f'Country: {country}, Instrument: {instrument}, Maturity: {maturity}')
                
                elif i['Yield'] != '':
                    to_db.append((i['Date'], country, instrument, maturity, float(i['Yield'])))

            cursor.executemany("INSERT INTO yields VALUES(?, ?, ?, ?, ?)", to_db)
            dbcon.commit()

def calculate_ns(maturity, b0, b1, b2, lm0):
    maturity_yield = (
        b0 + 
        b1 * ((1 - np.exp(-maturity / lm0)) / (maturity / lm0)) + 
        b2 * (((1 - np.exp(-maturity / lm0)) / (maturity / lm0)) - np.exp(-maturity / lm0)))
    return maturity_yield
                        
                    
with app.app_context():
    initialise_db()

@app.route("/")
@app.route("/latest")
def latest():
    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    maturity = 2.8

    result = cursor.execute('SELECT Maturity, Yield, Date FROM yields WHERE Country = "US" ORDER BY Date DESC LIMIT 9').fetchall()

    date = result[0][2]

    xdata = np.array([point[0] for point in result])
    ydata = np.array([point[1] for point in result])

    nspopt, pcov = curve_fit(calculate_ns, xdata, ydata, p0=[0.02, 0.01, 0.01, 1.0])

    ns_maturity_yield = calculate_ns(maturity, nspopt[0], nspopt[1], nspopt[2], nspopt[3])

    response = {
            "date":date,
            "country":"US",
            "maturity":maturity,
            "yield":ns_maturity_yield.round(4)
        }
    
    return response




