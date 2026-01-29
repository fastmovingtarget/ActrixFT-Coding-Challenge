import {type Latest } from "./Types/Types"

export const fetchLatest = async (
    country : 'US' | 'UK',
    maturity  : number,
    setYield : React.Dispatch<React.SetStateAction<Latest | null>>
) => {

    const returnPromise = new Promise<'Success' | 'Failure'>((resolve) => {
        fetch(
            `http://localhost:5000/latest?country=${country}&maturity=${maturity}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                }
            }
        ).then((rawData) => {
            rawData.json().then((data : Latest) => {
                setYield(data)
                resolve("Success")
            })
        })
    })
    return returnPromise;
}