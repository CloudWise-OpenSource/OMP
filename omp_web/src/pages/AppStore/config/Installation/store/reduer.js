import * as actionTypes from "./constants";

const defaultState = {
    dataSource:{}
};

function reducer(state = defaultState,action){
    switch(action.type){
        case actionTypes.CHANGE_DATASOURCE:
            return {...state, dataSource:action.payload.dataSource};
        default:
            return state;
    }
}

export default reducer;