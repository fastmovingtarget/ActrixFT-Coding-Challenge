# ActixFT Technical Test
## James Alport

## Installation Instructions:
 - install python packages:
    ```bash
        user@pc ~ActrixFT-Coding-Challenge $ cd PythonBackend
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ python -m venv .venv
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ source .venv/Scripts/activate
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ pip install flask
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ pip install flask_cors
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ pip install scipy
    ```
 - install React Packages:
    ```bash
        user@pc ~ActrixFT-Coding-Challenge $ cd ReactFrontend/ReactFrontend
        user@pc ~ActrixFT-Coding-Challenge/ReactFrontend/ReactFrontend $ npm install --save chart.js react-chartjs-2
    ```

## To Run
- Python:
    ```bash
        user@pc ~ActrixFT-Coding-Challenge/PythonBackend $ flask --app API.py run
    ```
- React:
    ```bash
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
    - Default maturity will be 10 years

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


## Implementation
- Performing the initial project setup and data read was simple but time-consuming.
    - CSV Data is read from files in ./PythonBackend/Data 
    - I chose to parse the Country/Instrument/Maturity values from the csv file's headers
    - The UK dates needed reformatting into ISO (YYYY-MM-DD) for SQLite's Date functions to work
- /latest
    - I ended up using defaults of Country=US and Maturity=10 for the latest, both in React and in Python
    - Putting together the initial /latest request went fairly smoothly, but even being familiar with it React takes a lot of time to code up
    - I also had some issues with CORS that required an additional package install, but with that it was easy to solve
- /timeseries 
    - fit curve code went in surprisingly easily - I'd done a lot of research on how to work it during my preparation
    - I ended up changing how I was querying the database - grouping the entries by date and 
    aggregating the Maturities and Yields into JSON arrays made for a much more efficient query than 
    just grabbing everything and LIMITing it to the number of data points needed
    - Interesting Error : fit_curve does not like the entry on October 1st 2022 SPECIFICALLY, I put in some generic error handling but that date
        was the only one that triggered it
    - Chart.js is once again both fun to work with and incredibly obtuse to start using
- /latestfit
    - During I was having trouble visualising how the fits were looking, so I decided to add in a graph to show how the interpolated values for the /latest query were found
    - It also balances well visually, allowing both the /latest and /timeseries sections to have nice graphs to them
- Styling
    - I find it best to style when I've got everything on the page that I need - styling's relaxing, but easy to lose track of time

## Future Steps
### Backend API
- Error handling for non-parsable query strings (completed post-walkthrough)
    - Priority 1, should be a fairly simple to handle the error gracefully. I can't believe I didn't consider it.
- Source the data programatically
    - Having a daily tick on the backend to source the most recent data set would be a much better solution than the manual download I'm using now
- Use Pandas for better data handling
- Handle Month/MO units in maturity requests (completed post-walkthrough)
    - Obviously if I'm only running requests from the frontend they're not needed, but a REST API should be able to handle requests outside of the frontend
- Handle non-standard dates in timeseries requests
    - Similar to Maturity, I can't expect to be working with sanitised requests so I need to be able to handle a variety
- Improve British Gilt dataset
    - The data to make more accurate interpolation is clearly there as a curve is available on the BoE website, but I clearly need to do some hunting to find it

### Frontend Site
- Fix error where user is unable to enter decimals on the frontend maturity request (completed post-walkthrough)
- Improve Styling, Colours, implement a light/dark mode toggle
- Graphs - Label Axis, improve axis ticks
- Add a scatter to the fit curve to show the actual data values that we're interpolating with
- Add possibility for multiple maturities on the time series graph (which would take an age to load, but very interesting to view)