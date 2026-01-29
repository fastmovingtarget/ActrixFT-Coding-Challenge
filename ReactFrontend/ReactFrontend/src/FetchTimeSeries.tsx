import {type TimeSeries } from "./Types/Types"

export const fetchTimeSeries = async (
    country : 'US' | 'UK',
    maturity  : number,
    startDate : Date,
    endDate : Date,
    setTimeSeries : React.Dispatch<React.SetStateAction<TimeSeries | null>>
) => {

    const returnPromise = new Promise<'Success' | 'Failure'>((resolve) => {
        
        fetch(
            `http://localhost:5000/timeseries?country=${country}&maturity=${maturity}&start_date=${startDate.toISOString().substring(0,10)}&end_date=${endDate.toISOString().substring(0,10)}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            }
        ).then((rawData) => {
            rawData.json().then((data) => {
                setTimeSeries(data)
                resolve("Success")
            })
        })
    })
    return returnPromise;
}