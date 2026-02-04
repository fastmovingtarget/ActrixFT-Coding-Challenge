export interface Latest {
    Date : string,
    Country : "US" | "UK",
    Maturity : number,
    Yield : number
}

export interface LatestFit {
    Curve: 'ns' | 'linear',
    Constants: number[],
    MaturityData: number[],
    YieldData: number[]
}

export interface TimeSeries {
    Country : "US" | "UK",
    Maturity : number,
    Data : [TimeSeriesPoint]
}

export interface TimeSeriesPoint {
    Date : string,
    Yield : number
}