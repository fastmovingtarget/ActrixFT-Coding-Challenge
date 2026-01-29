import {type Latest } from "./Types/Types"

export const fetchLatest = async (
    country : 'US' | 'UK',
    maturity  : number,
    setYield : React.Dispatch<React.SetStateAction<Latest | null>>
) => {

    const returnPromise = new Promise<'Success' | 'Failure'>((resolve) => {
        console.log("Getting Data")
        fetch(
            `http://localhost:5000/latest?country=${country}&maturity=${maturity}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            }
        ).then((rawData) => {
            console.log(rawData)
            rawData.json().then((data : Latest) => {
                console.log(data)
                setYield(data)
                resolve("Success")
            })
        })
    })
    return returnPromise;
}