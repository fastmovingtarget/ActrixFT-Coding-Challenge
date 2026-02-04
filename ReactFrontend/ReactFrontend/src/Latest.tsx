import { useEffect, useState } from 'react'
import { type Latest, type LatestFit } from './Types/Types';
import { fetchLatest } from './FetchLatest';
import { fetchLatestFit } from './FetchLatestFit';
import LatestFitGraph from './LatestFitGraph';
import { Failed, Loading } from './Placeholders';

export function Latest(){
    const [maturity, setMaturity] = useState<number>(10.0);
    const [country, setCountry] = useState<"US" | "UK">("US")
    const [latest, setLatest] = useState<Latest | null>(null);
    const [latestFit, setLatestFit] = useState<LatestFit | null>(null)
    const [loadStatus, setLoadStatus] = useState<"Loading" | "Success" | "Failure">("Loading")

    useEffect(() => {
        fetchLatestFit(country, setLatestFit).then((result) => setLoadStatus(result))
    },[country])
    
    useEffect(() => {
        fetchLatest("US", 10.0, setLatest).then((result) => setLoadStatus(result))
    }, [])

    return (
        <div className="latest main-container row">
            <div className="column">
                <p className="title">Latest Yield Data:</p>
                <div>
                    <button className={`button ${country === "US" && 'active'}`} onClick={() => setCountry("US")}>US</button>
                    <button className={`button ${country === "UK" && 'active'}`} onClick={() => setCountry("UK")}>UK</button>
                </div>  
                <div>
                    <label>Set Maturity (0.0 - 50.0): 
                        <input type="number" id="latest-maturity-input" name="latest-maturity-input" min="0" max="50" defaultValue="10" step="any" onChange={(event) => {
                            if(event.target.checkValidity())
                                setMaturity(parseFloat(event.target.value) || 0.0)
                            else
                                event.target.value = `${maturity}`
                        }}/>
                    </label>
                </div>    
                <p>Date: {latest?.Date}</p>
                <p>Yield: {latest?.Yield}</p>
                <button onClick={() => {
                    setLoadStatus("Loading")
                    fetchLatest(country, maturity, setLatest).then((result) => setLoadStatus(result))
                }} >Get Latest Yield</button>
            </div>
            <div className="column graph-container">
                {
                    latestFit && latest && loadStatus === "Success" ? 
                    <LatestFitGraph latestFit={latestFit} latest={latest}/>:
                    loadStatus === "Loading" ? 
                    <Loading loading={loadStatus === "Loading"}/> : 
                    <Failed failed={loadStatus === "Failure"}/>
                }
            </div>
        </div>
    )
}