import * as actionTypes from "./constants";

const defaultState = {
  dataSource: {},
  ipList: [],
  step1Data: {
    basic:[],
    dependence:[]
  },
  step2Data: {},
  errorList:[],

  step3Data: []
};

function reducer(state = defaultState, action) {
  switch (action.type) {
    case actionTypes.CHANGE_DATASOURCE:
      return { ...state, dataSource: action.payload.dataSource };
    case actionTypes.CHANGE_IPLIST:
      return { ...state, ipList: action.payload.ipList };
    case actionTypes.CHANGE_STEP1DATA:
      return { ...state, step1Data: action.payload.step1Data };
    case actionTypes.CHANGE_STEP2DATA:
      return { ...state, step2Data: action.payload.step2Data };
      case actionTypes.CHANGE_STEP2ERRORLISTDATA:
        return { ...state, errorList: action.payload.errorList };
    case actionTypes.CHANGE_STEP3DATA:
      return { ...state, step3Data: action.payload.step3Data };
    default:
      return state;
  }
}

export default reducer;
