/*
 * @Author: your name
 * @Date: 2021-06-13 15:59:12
 * @LastEditTime: 2021-06-22 17:31:22
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp_fontend/src/pages/ProductsManagement/VersionManagement/InstallationDetails/store/reduer.js
 */

import * as actionTypes from "./constants";

const defaultState = {
    hostTotal: 0,
    serviceTotal: 0
};

function reducer(state = defaultState,action){
    switch(action.type){
        case actionTypes.CHANGE_ABNORMALHOSTNUMBER:
            return {...state, hostTotal: action.payload.host};
        case actionTypes.CHANGE_ABNORMALSERVICENUMBER:
            return {...state, serviceTotal: action.payload.service};
        default:
            return state;
    }
}

export default reducer;