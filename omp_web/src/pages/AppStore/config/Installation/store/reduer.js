import * as actionTypes from "./constants";

const defaultState = {
    dataSource:{},
    ipList:[]
};

function reducer(state = defaultState,action){
    switch(action.type){
        case actionTypes.CHANGE_DATASOURCE:
            return {...state, dataSource:action.payload.dataSource};
        case actionTypes.CHANGE_IPLIST:
            return {...state, ipList:action.payload.ipList};
        default:
            return state;
    }
}

export default reducer;