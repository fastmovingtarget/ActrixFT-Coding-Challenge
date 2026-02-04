import {type LatestFit } from "./Types/Types"

export const fetchLatestFit = async (
    country : 'US' | 'UK',
    setLatestFit : React.Dispatch<React.SetStateAction<LatestFit | null>>
) => {

    const returnPromise = new Promise<'Success' | 'Failure'>((resolve) => {
        fetch(
            `http://localhost:5000/latestfit?country=${country}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            }
        ).then((rawData) => {
            rawData.json().then((data : LatestFit) => {
                data.Constants = data.Constants.map((constant) => Number(constant))

                setLatestFit(data)
                resolve("Success")
            })
        })
    })
    return returnPromise;
}