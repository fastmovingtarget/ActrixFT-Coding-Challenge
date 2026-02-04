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
import { Chart } from 'react-chartjs-2';
import { type LatestFit, type Latest } from './Types/Types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);


export default function LatestFitGraph ({latestFit, latest} : {latestFit : LatestFit, latest : Latest}) {

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
                display: false
            },
            title: {
                display: true,
                text: `Interpolation Curve for ${latest.Date}`,
            },
        },
        interaction:{
            mode:"nearest",
        },
        scales:{
            y:{
                title:{
                    display:true,
                    text: "Yield"
                }
            },
            x:{
                title:{
                    display:true,
                    text: "Maturity"
                }
            }
        }
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

    const scatterData = latestFit.MaturityData.map((maturity, index) => {
        return [maturity, latestFit.YieldData[index]]
    })

    const dataset = new Array(600).fill(0).map((_, index) => {
        const maturity = (index + 1)/12;
        const m_yield = findYield(maturity)
        return [maturity.toFixed(2), m_yield]
    })

    const data = {
        labels: [0, 60],
        datasets: [
            {
                data: dataset,
                borderColor: 'rgb(99, 132, 255)',
                pointRadius: 0.5,
                order:2
            },
            {
                data:scatterData,
                backgroundColor: 'rgb(255, 132, 99)',
                order:1
            }
        ],
    };


//technically we're drawint 2 scatter plots, but the scatter points of the fit curve are so close together they're indistinguishable froma  line
    return <>
        <Chart type="scatter" options={options} data={data}/>
    </>
}