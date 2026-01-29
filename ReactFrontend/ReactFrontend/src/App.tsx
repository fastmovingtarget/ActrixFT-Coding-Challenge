import './App.css'
import { Latest } from './Latest';
import { TimeSeries } from './TimeSeries';

function App() {
  return (
    <div style={{display:'flex', flexDirection:"column", height:"100%"}}>  
        <header>
          ActrixFT Test Data
        </header>
        <div className='column body-container'>
          <Latest/>
          <TimeSeries/>
        </div>
        <footer>
          By James Alport
        </footer>
    </div>
  )
}

export default App