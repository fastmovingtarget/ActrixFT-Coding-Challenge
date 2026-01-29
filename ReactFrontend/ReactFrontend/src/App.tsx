import { useEffect, useState } from 'react'
import { fetchLatest } from './FetchLatest';
import './App.css'
import type { Latest } from './Types/Types';

function App() {

  const [maturity, setMaturity] = useState<number>(10.0);
  const [country, setCountry] = useState<"US" | "UK">("US")
  const [latest, setLatest] = useState<Latest | null>(null);

  useEffect(() => {
    if(maturity != 0.0)
      fetchLatest(country, maturity, setLatest)
  }, [maturity, country])

  return (
  <div>  
      <header>
        ActrixFT Test Data
      </header>
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
      <footer>
        By James Alport
      </footer>
  </div>
  )
}

export default App