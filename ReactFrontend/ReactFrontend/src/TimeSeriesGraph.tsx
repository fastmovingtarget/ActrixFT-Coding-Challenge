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
import { type TimeSeries } from './Types/Types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);


export default function TimeSeries ({timeSeries} : {timeSeries : TimeSeries}) {

    const options = {
        responsive: true,
        plugins: {
            legend: {
                display:false,
                position: 'top' as const,
            },
            title: {
            display: true,
            text: `Country : ${timeSeries.Country}, Maturity : ${timeSeries.Maturity}`,
            },
        },
    };

    const dataset = timeSeries.Data.map((dataItem) => [dataItem.Date, dataItem.Yield])

    const data = {
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