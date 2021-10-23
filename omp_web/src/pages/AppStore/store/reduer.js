import * as actionTypes from "./constants";

const defaultState = {
    appStoreTabKey:"component"
};

function reducer(state = defaultState,action){
    switch(action.type){
        case actionTypes.CHANGE_APPSTORETABKEY:
            return {...state, appStoreTabKey: action.payload.appStoreTabKey};
        default:
            return state;
    }
}

export default reducer;