import {  useState } from 'react'
import { fetchLatest } from './FetchLatest';
import {fetchTimeSeries} from './FetchTimeSeries'
import './App.css'
import { type TimeSeries, type Latest } from './Types/Types';
import TimeSeriesGraph from './TimeSeries';

function App() {

  const [maturity, setMaturity] = useState<number>(10.0);
  const [country, setCountry] = useState<"US" | "UK">("US")
  const [latest, setLatest] = useState<Latest | null>(null);
  const [startDate, setStartDate] = useState<Date>(new Date());
  const [endDate, setEndDate] = useState<Date>(new Date())
  const [timeSeries, setTimeSeries] = useState<TimeSeries | null>(null)

  return (
    <div>  
        <header>
          ActrixFT Test Data
        </header>
        <div>
          <div>
            <button onClick={() => setCountry("US")}>US</button>
            <button onClick={() => setCountry("UK")}>UK</button>
          </div>  
            <input type="number" id="1" name="1" min="0" max="50" onChange={(event) => {
              setMaturity(parseFloat(event.target.value) || 0.0)
            }}/>
          <div>      
            Date: {latest?.Date}
            Maturity : {latest?.Maturity}, Yield: {latest?.Yield}
          </div>
            <input type="button" onClick={() => fetchLatest(country, maturity, setLatest)}/>
        </div>
        <div>
            <label>
              Start Date:
              <input 
                id="start-date"
                name="end-date"
                type="date"
                defaultValue={new Date().getDate()}
                min={"2016-02-01"}
                max={new Date().toISOString().substring(0,10)}
                onChange={(e) => setStartDate(new Date(e.target.value))}
              />
            </label>
            <label>
              End Date:
              <input 
                id="end-date"
                name="end-date"
                type="date"
                defaultValue={new Date().getDate()}
                min={"2016-02-01"}
                max={new Date().toISOString().substring(0,10)}
                onChange={(e) => setEndDate(new Date(e.target.value))}
              />
            </label>
            <input type="button" onClick={() => fetchTimeSeries(country, maturity, startDate, endDate, setTimeSeries)}/>
          {
            timeSeries !== null ? 
              <TimeSeriesGraph timeSeries={timeSeries}/> : 
              <></>
          }
        </div>
        <footer>
          By James Alport
        </footer>
    </div>
  )
}

export default App