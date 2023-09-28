import * as actionTypes from "./constants";

const defaultState = {
    isMaintenance:false
};

function reducer(state = defaultState,action){
    switch(action.type){
        case actionTypes.CHANGE_MAINTENANCE:
            return {...state, isMaintenance: action.payload.isMaintenance};
        case actionTypes.CHANGE_REFRESHTIME:
            return {...state, time: action.payload.time};
        default:
            return state;
    }
}

export default reducer;