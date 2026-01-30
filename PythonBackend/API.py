import sqlite3, csv, os, json, numpy as np
from flask import Flask, request
from flask_cors import CORS
from scipy.optimize import curve_fit
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def initialise_db():
    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    # Check to see if the database has already be initialised, return if it has
    res = cursor.execute(f'SELECT name FROM sqlite_master')
    if res.fetchone() is not None:
        print("Database already initialised")
        return

    cursor.execute("CREATE TABLE yields (Date TEXT, Country TEXT, Instrument TEXT, Maturity REAL, Yield REAL)")

    # Check through every file in ./Data
    for file in os.listdir('./Data'):
        with open(f'./Data/{file}', 'r') as fileData:
            dr = csv.DictReader(fileData, fieldnames=['Date', 'Yield'])
            to_db = []
            country = 0
            instrument = ""
            maturity = 0.0
            for i in dr:
                # if any of the constants haven't been populated for this csv
                if country == "" or instrument == "" or maturity == 0.0:
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
                
                # Just don't read the values that are blank/null
                elif i['Yield'] != '':
                    # UK dates are NOT in ISO format, so we have to strip and reformat them
                    if country == "UK":
                        newDate = datetime.strptime(i['Date'], "%d %b %y").strftime("%Y-%m-%d")
                        to_db.append((newDate, country, instrument, maturity, float(i['Yield'])))
                    else:
                        to_db.append((i['Date'], country, instrument, maturity, float(i['Yield'])))

            cursor.executemany("INSERT INTO yields VALUES(?, ?, ?, ?, ?)", to_db)
            dbcon.commit()

def calculate_ns(maturity, b0, b1, b2, lm0):
    maturity_yield = (
        b0 + 
        b1 * ((1 - np.exp(-maturity / lm0)) / (maturity / lm0)) + 
        b2 * (((1 - np.exp(-maturity / lm0)) / (maturity / lm0)) - np.exp(-maturity / lm0)))
    return maturity_yield

def calculate_linear(maturity, grad, const):
    maturity_yield = (
        const + 
        maturity*grad
    )
    return maturity_yield

# finds the yield for a given maturity and dataset (which is a function of Date)
def find_yield(maturity, xdata, ydata):
    yield_out = 0.0
    #check to see if the requested maturity is in the data set, if it is then we don't have to worry about extrapolating/interpolating
    for i in range(len(xdata)):
        if xdata[i] == float(maturity):
            return ydata[i]
        
    # The Brits don't really give enough useful data (only 3 points) to plot a complex NS interpolation curve. They get a simple linear curve instead
    if(len(xdata) > 3):
        nspopt, pcov = curve_fit(calculate_ns, xdata, ydata, p0=[0.02, 0.01, 0.01, 1.0])
        yield_out = calculate_ns(float(maturity), nspopt[0], nspopt[1], nspopt[2], nspopt[3]).round(4)
    else: 
        linpopt, pcov = curve_fit(calculate_linear, xdata, ydata, p0=[0.02, 0.01])
        yield_out = calculate_linear(float(maturity), linpopt[0], linpopt[1]).round(4)

    return yield_out

# Finds the fit constants and the curve type
def find_fit(xdata, ydata):
    if(len(xdata) > 3):
        nspopt, pcov = curve_fit(calculate_ns, xdata, ydata, p0=[0.02, 0.01, 0.01, 1.0])
        return {
            "Curve":"ns",
            "Constants":[f'{nspopt[0]}', f'{nspopt[1]}', f'{nspopt[2]}', f'{nspopt[3]}']
        }
    else: 
        linpopt, pcov = curve_fit(calculate_linear, xdata, ydata, p0=[0.02, 0.01])
        return {
            "Curve":"linear",
            "Constants":[linpopt[0], linpopt[1]]
        }

# Maturity can be given 
def parse_maturity(maturity):
    default  = '10'
    divider = 1
    maturity_out = maturity
    if maturity.lower().endswith("mo") or maturity.lower().endswith("month") or maturity.lower().endswith("months"):
        divider = 12
        maturity_out = f'{maturity.lower().split("mo")[0]}'
        
    try:
        maturity_float = float(maturity_out)/divider
        return f'{maturity_float}'
    except:
        print(f"Error Parsing maturity: {maturity}, returning {default}")
        return default

                          
with app.app_context():
    initialise_db()

@app.route("/")
@app.route("/latest")
def latest():
    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    maturity = parse_maturity(request.args.get('maturity', '10'))
    country = request.args.get('country', 'US')

    if country != "US" or country != "UK":
        country = "US"

    result = cursor.execute(
        ''' SELECT 
                json_group_array(Maturity) Maturities, 
                json_group_array(Yield) Yields, 
                Date 
            FROM yields 
            WHERE Country = ? 
            GROUP BY Date
            ORDER BY Date DESC LIMIT 1''', [country]).fetchall()[0]#there's only 1 result, so we can specify the first result here

    xdata = json.loads(result[0])
    ydata = json.loads(result[1])

    maturity_yield = find_yield(maturity, xdata, ydata)

    response = {
            "Date":result[2],
            "Country":country,
            "Maturity":maturity,
            "Yield": f'{maturity_yield}'
        }
            
    return response

# I wanted to draw the currently used regression curve in the client, so I put in a function to find the fit curve equation
@app.route('/latestfit')
def latestfit():
    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    country = request.args.get('country', 'US')
    if country != "US" or country != "UK":
        country = "US"

    result = cursor.execute(
        ''' SELECT 
                json_group_array(Maturity) Maturities, 
                json_group_array(Yield) Yields, 
                Date 
            FROM yields 
            WHERE Country = ? 
            GROUP BY Date
            ORDER BY Date DESC LIMIT 1''', [country]).fetchall()[0]#there's only 1 result, so we can specify the first result here

    xdata = json.loads(result[0])
    ydata = json.loads(result[1])

    fit = find_fit(xdata, ydata)

    return fit

@app.route("/timeseries")
def timeseries():
    start_date_default = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', start_date_default)
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))

    maturity = parse_maturity(request.args.get('maturity', '10'))
    country = request.args.get('country', 'US')

    if country != "US" or country != "UK":
        country = "US"

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except:
        print(f"invalid start date, defaulting to: {start_date_default}")
        start_date = start_date_default

    try:
        datetime.strptime(end_date, "%Y-%m-%d")
    except:
        print(f"invalid end date, defaulting to: {datetime.today().strftime('%Y-%m-%d')}")
        end_date = datetime.today().strftime('%Y-%m-%d')

    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    result = cursor.execute(
        '''SELECT 
            json_group_array(Maturity) Maturities,
            json_group_array(Yield) Yields,
            Date 
            FROM yields 
            WHERE Country = ? 
            AND DATE BETWEEN ? AND ?
            GROUP BY Date
            ORDER BY Date DESC''', [country, start_date, end_date]).fetchall()
    
    date_data = []

    for date_set in result:
        xdata = json.loads(date_set[0])
        ydata = json.loads(date_set[1])
        try:
            maturity_yield = find_yield(maturity, xdata, ydata)
        except:
            print(f"An error occurred with the {country} data on {date_set[2]}")
        else:
            date_data.append({
                "Date": date_set[2],
                "Yield": f'{maturity_yield}'
            })

    response = {
            "Country":country,
            "Maturity":maturity,
            "Data":date_data
    }


    return response






