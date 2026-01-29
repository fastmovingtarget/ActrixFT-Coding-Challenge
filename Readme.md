# ActixFT Technical Test
## James Alport

## Installation Instructions:
 - install python packages:
    ```console
        user@pc ~ActrixFT-Coding-Challenge $ cd PythonBackend
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ pip install flask
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ pip install flask_cors
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ pip install scipy
    ```
 - install React Packages:
    ```console
        user@pc ~ActrixFT-Coding-Challenge $ cd ReactFrontend/ReactFrontend
        user@pc ~ActrixFT-Coding-Challenge/ReactFrontend/ReactFrontend $ npm install --save chart.js react-chartjs-2
    ```

## To Run
    ```console
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ flask --app API.py run
    ```
    ```console
        user@pc ~ActrixFT-Coding-Challenge/ReactFrontend/ReactFrontend $ npx vite dev
    ```

## Planning
### API
    - Python
    - Flask API
    - SciPy for curve fitting
    - GET /latest?country=["US"|"UK"]&maturity=[years : float (e.g. 2.5)]
        - response JSON {
            "date":"2026/01/29"
            "country":"US"|"UK"
            "maturity":2.5
            "yield":0.0423
        }
        - "date" will be the most recent past entry to today (so if today is a weekend, return friday's result instead)
        - "yield" requires curve fit for a single set of points for the "date"
        - in the end the output is just a number and a date. Easy to display, efficient to extract

    - GET /timeseries?country=US|UK&maturity=(float)&start_date=(date)&end_date=(date)
        response JSON { 
            "country":"US"|"UK"
            "maturity":(float)
            "data":[
                {"date" : (start_date), "yield"=(float)}
                {"date" : (start_date + 1), "yield"=(float)}
                ...
                {"date" : (end_date), yield=(float)}
            ]
        }
    - output is multiple yields over multiple dates, which will (outside of the specific source data points) involve 1 curve fit for each date.
        - Efficiency will be a massive issue for large date ranges - may have to make decisions on what kind of fit to use based on those efficiency stats

### Database and Dataset
    - SQLite Database
        - I'm using SQLite for familiarity, but wouldn't necessarily recommend a Relational Database Management System (RMDBS) as there's no relationship between tables...because there's only one table!
    - Pre-Sourced CSV files
        - I'd say it's out of scope at present but I'd like to be able to automate getting the data on a day-to-day basis without re-starting the API/Database.
        - When reading CSV files just skip the entries with no yield value
    - Dataset sourced from:
        - US: 
            - FRED
            - "Market Yield on U.S. Treasury Securities at [X]-{Year | Month} Constant Maturity, Quoted on an Investment Basis"
            - e.g. https://fred.stlouisfed.org/series/DGS30 or https://fred.stlouisfed.org/series/DGS3MO
            - X is the maturity, in this dataset it can be 1, 3 or 6 months or 1, 2, 5, 10, 30 years
        - UK: 
            - "Yield from British Government Securities, X year Nominal Par Yield"
            - X can be 5, 10 or 20 years
            - I chose Nominal Par Yield because it had a day-to-day breakdown which is more in line with the data that will likely be requested. Nominal Zero-Coupon yields only had month average or end-of-month yield values
    
    
### React Frontend
    - I'll have to swallow a little bit of pride and rush this out - the backend is more important right now
    - /latest: 
        - Buttons for the US/UK setting, and a numerical form for the requested maturity
        - On initial load, fetch data for /latest using default settings just as an example
        - For the moment let's say defaults are US and 5 years
        - Cache the previous settings in localstorage
        - I'd like to have a plot for today's maturity fit, but that's an extra API call. Let's make that a stretch goal
    - /timeseries:
        - Line graph of the time series
        - Separated button for US/UK, form for maturity
        - Date range shouldn't go past 10 years ago
        - Have a loading animation for when the fetch call takes time to return
        - I will absolutely have the default be a maturity value I don't have to generate a fit curves for! Let's say 10 years

### Task Breakdown and Time Estimates
    - Code for reading CSV files into sqlite - 1 hour,
    - /latest
        - code for reading latest data and fitting a curve to it - 30 mins
        - code for finding yield for a given maturity - 30 mins
        - Initialise React App and build a basic fetch, then display data in text form - 1 hour
    - /timeseries
        - code to generate a fit curve for each selected date - 1 hour
        - return the correct maturity for each date - 30 mins
        - Plot Line chart using that data in React - 1 hour
    - /latestfit
        - return the fit constants for the latest date and the data points to be used in the scatter - 15 mins
        - Plot the graph out in Chart.js - 1 hour
    - finish up, test and polish - 1 hour 45 mins