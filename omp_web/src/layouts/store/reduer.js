import * as actionTypes from "./constants";

const defaultState = {
    viewSize:{ height:0, width:0 },   
    a:"1"
};

function reducer(state = defaultState,action){
    switch(action.type){
        case actionTypes.SET_VIEWSIZE:
            return {...state, viewSize: action.payload.viewSize};
        case "c":
            return {...state, a: "123"};
        default:
            return state;
    }
}

export default reducer;