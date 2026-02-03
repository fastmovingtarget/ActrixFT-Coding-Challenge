import sqlite3, csv, os, json, numpy as np, pandas as pd
from flask import Flask, request
from flask_cors import CORS
from scipy.optimize import curve_fit
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

df = None

def initialise_db():
    dbcon = sqlite3.connect('yields.db')
    cursor = dbcon.cursor()

    # Check to see if the database has already be initialised, return if it has
    res = cursor.execute(f'SELECT name FROM sqlite_master')
    if res.fetchone() is not None:
        return

    dfarray = []

    # Check through every file in ./Data
    for file in os.listdir('./Data'):
        dataframe = pd.read_csv(f'./Data/{file}')
        country = 0
        instrument = ""
        maturity = 0.0
        if 'DGS' in dataframe.columns[1]:
            country = 'US'
            instrument = 'Treasury'
            maturityStr = dataframe.columns[1].split("DGS")[1]
            if(maturityStr.endswith("MO")):
                maturity = float(maturityStr.split("MO")[0])/12.0
            else:
                maturity = float(maturityStr)
        if 'British' in dataframe.columns[1]:
            country = 'UK'
            instrument = 'Gilt'
            if '5' in dataframe.columns[1]:
                maturity = 5
            elif '10' in dataframe.columns[1]:
                maturity = 10
            elif '20' in dataframe.columns[1]:
                maturity = 20
            dataframe['Date'] = dataframe['Date'].map(format_date)

        dataframe.rename(columns={dataframe.columns[0] : "Date", dataframe.columns[1] : "Yield"}, inplace = True)
        dataframe.insert(1, "Maturity", maturity)
        dataframe.insert(1, "Instrument", instrument)
        dataframe.insert(1, "Country", country)

        dfarray.append(dataframe)
            

        print(f'Country: {country}, Instrument: {instrument}, Maturity: {maturity}')


    df = pd.concat(dfarray)

    df = df.dropna()

    df["Date"] = pd.to_datetime(df["Date"])
    df['Date'] = df['Date'].dt.date

    if(df is None):
        print("Error importing data: Data Frame not assigned")
        return

    df.to_sql(name="yields", con=dbcon)

def format_date(old_date):
    return datetime.strptime(old_date, "%d %b %y").strftime("%Y-%m-%d")

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
def find_yield(maturity, xdata, ydata, params = []):
    yield_out = 0.0
    #check to see if the requested maturity is in the data set, if it is then we don't have to worry about extrapolating/interpolating
    for i in range(len(xdata)):
        if xdata[i] == float(maturity):
            return ydata[i], []
                
    # The Brits don't really give enough useful data (only 3 points) to plot a complex NS interpolation curve. They get a simple linear curve instead
    if(len(xdata) > 3):
        if(len(params) == 0):
            params = [0.1, 0.1, 0.1, 1.0]
        paramopts, pcov = curve_fit(calculate_ns, xdata, ydata, p0=params)
        yield_out = calculate_ns(float(maturity), paramopts[0], paramopts[1], paramopts[2], paramopts[3]).round(4)
    else: 
        paramopts, pcov = curve_fit(calculate_linear, xdata, ydata)
        yield_out = calculate_linear(float(maturity), paramopts[0], paramopts[1]).round(4)

    return yield_out, paramopts

# Finds the fit constants and the curve type
def find_fit(xdata, ydata):
    if(len(xdata) > 3):
        nspopt, pcov = curve_fit(calculate_ns, xdata, ydata, p0=[0.1, 0.1, 0.1, 1.0])
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
    df = pd.read_sql("SELECT * FROM yields", dbcon)

    maturity = parse_maturity(request.args.get('maturity', '10'))
    country = request.args.get('country', 'US')

    if country != "US" or country != "UK":
        country = "US"
    
    result = df[(df["Date"] == df["Date"].max()) & (df["Country"] == country)]

    xdata = result["Maturity"].values
    ydata = result["Yield"].values

    maturity_yield, params = find_yield(maturity, xdata, ydata)

    response = {
            "Date":df["Date"].max(),
            "Country":country,
            "Maturity":maturity,
            "Yield": f'{maturity_yield}'
        }
            
    return response

# I wanted to draw the currently used regression curve in the client, so I put in a function to find the fit curve equation
@app.route('/latestfit')
def latestfit():
    dbcon = sqlite3.connect('yields.db')
    df = pd.read_sql("SELECT * FROM yields", dbcon)

    country = request.args.get('country', 'US')
    if country != "US" or country != "UK":
        country = "US"

    result = df[(df["Date"] == df["Date"].max()) & (df["Country"] == country)]

    xdata = result["Maturity"].values
    ydata = result["Yield"].values

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

    df = pd.read_sql("SELECT * FROM yields", dbcon)
    result = df[(df["Date"] > start_date) & (df["Date"] < end_date)  & (df["Country"] == country)]
    result_grouped = result.groupby(result["Date"])

    result_frame = result_grouped[["Maturity", "Yield"]].apply(pd.DataFrame)
   
    date_data = []
#
    params = []
    for date in result_grouped.groups:
        xdata = result_frame.loc[date]["Maturity"].values
        ydata = result_frame.loc[date]["Yield"].values
           
        try:
            if(len(params) == 0):
                maturity_yield, paramopts = find_yield(maturity, xdata, ydata)
                params = paramopts
            else:
                maturity_yield, paramopts = find_yield(maturity, xdata, ydata, params)
        except Exception as e:
            print(f"Error: {e} occurred with the {country} data on {date}")
        else:
            date_data.append({
                    "Date": date,
                    "Yield": f'{maturity_yield}'
                })

    response = {
            "Country":country,
            "Maturity":maturity,
            "Data":date_data
    }


    return response






