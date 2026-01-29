import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { type LatestFit } from './Types/Types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);


export default function LatestFitGraph ({latestFit} : {latestFit : LatestFit}) {

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
                display: false
            },
            title: {
                display: true,
                text: 'Maturity Fit Curve',
            },
        },
    };

    const findYield = (maturity : number) => {
        if(latestFit.Curve === "ns"){
            return (
                latestFit.Constants[0] + 
                latestFit.Constants[1] * ((1 - Math.exp(-maturity / latestFit.Constants[3])) / (maturity / latestFit.Constants[3])) + 
                latestFit.Constants[2] * (((1 - Math.exp(-maturity / latestFit.Constants[3])) / (maturity / latestFit.Constants[3])) - Math.exp(-maturity / latestFit.Constants[3]))
            )
        }
        else
            return (
                latestFit.Constants[0]*maturity + latestFit.Constants[1]
            )
    }

    const dataset = new Array(600).fill(0).map((_, index) => {
        const maturity = (index + 1)/12;
        const m_yield = findYield(maturity)
        return [maturity.toFixed(2), m_yield]
    })

    const data = {
        labels: [0,5,10,15,20,25,30,35,40,45,50,55,60],
        datasets: [
            {
                data: dataset,
                borderColor: 'rgb(99, 132, 255)',
            }
        ],
    };



    return <>
        <Line options={options} data={data}/>
    </>
}