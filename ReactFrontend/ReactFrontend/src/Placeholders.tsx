import { ClipLoader } from "react-spinners";

export function Loading({loading} : {loading : boolean}){
    return <ClipLoader
        color={"#999999"}
        loading={loading}
        
    />
}

export function Failed({failed} : {failed : boolean}){
    return failed ? (
        <p>Unable to load data, please try again in a few minutes</p>
    ) : 
    null 
    
}