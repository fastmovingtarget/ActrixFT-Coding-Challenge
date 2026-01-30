import { useState, useEffect } from 'react'

import {fetchTimeSeries} from './FetchTimeSeries'
import TimeSeriesGraph from './TimeSeriesGraph';

import { type TimeSeries} from './Types/Types';

export function TimeSeries(){

    const prevMonth = new Date();
    prevMonth.setMonth(new Date().getMonth() - 1)

    const [startDate, setStartDate] = useState<Date>(prevMonth);
    const [endDate, setEndDate] = useState<Date>(new Date())
    const [maturity, setMaturity] = useState<number>(10.0);
    const [country, setCountry] = useState<"US" | "UK">("US")
    const [timeSeries, setTimeSeries] = useState<TimeSeries | null>(null)

    useEffect(() => {
        const prevMonthDefault = new Date();
        prevMonthDefault.setMonth(new Date().getMonth() - 1)
        fetchTimeSeries("US", 10, prevMonthDefault, new Date(), setTimeSeries)
    }, [])


    return (
        <div className="time-series main-container row">
            <div className="column">
                <p className="title">Time Series Yield Data:</p>
                <div>
                    <button className={`button ${country === "US" && 'active'}`} onClick={() => setCountry("US")}>US</button>
                    <button className={`button ${country === "UK" && 'active'}`} onClick={() => setCountry("UK")}>UK</button>
                </div>  
                <label>Set Maturity (0.0 - 50.0): 
                    <input type="number" id="1" name="1" min="0" max="50" defaultValue="10" step="any" onChange={(event) => {
                        if(event.target.checkValidity())
                            setMaturity(parseFloat(event.target.value) || 0.0)
                        else
                            event.target.value = `${maturity}`
                            
                    }}/>
                </label>
                <label>
                Start Date:
                <input 
                    id="start-date"
                    name="end-date"
                    type="date"
                    defaultValue={prevMonth.toISOString().substring(0,10)}
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
                    defaultValue={new Date().toISOString().substring(0,10)}
                    min={"2016-02-01"}
                    max={new Date().toISOString().substring(0,10)}
                    onChange={(e) => setEndDate(new Date(e.target.value))}
                />
                </label>
                <button onClick={() => fetchTimeSeries(country, maturity, startDate, endDate, setTimeSeries)}>Get Time Series Data</button>
            </div>
            <div className="column graph-container">
                {
                    timeSeries !== null ? 
                    <TimeSeriesGraph timeSeries={timeSeries}/> : 
                    <></>
                }
            </div>
        </div>
    )
}