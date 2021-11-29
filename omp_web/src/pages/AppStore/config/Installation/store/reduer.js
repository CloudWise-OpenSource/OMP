import * as actionTypes from "./constants";
import * as R from "ramda";

const defaultState = {
  dataSource: {},
  ipList: [],
  step1Data: {
    basic: [],
    dependence: [],
  },
  step2Data: {},
  errorList: [],

  step3Data: {},
  // step3Data数据结构
  // {
  //    ip10.012.1:[{
  //       name:doucZabbixApi
  //       log_dir:/abc/d,
  //        ...
  //    },
  //    ...]
  //  }
  step3ErrorData: {},
};

function reducer(state = defaultState, action) {
  const stateCopy = R.clone(state);
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
      if(!action.payload.ipData){
        return {
          ...state,
          step3Data:{}
        }
      }
      return {
        ...state,
        step3Data: {
          ...state.step3Data,
          ...action.payload.ipData,
        },
      };
    case actionTypes.CHANGE_STEP3SERVERDATA:
      let { ip, name, key, value } = action.payload;
      let serviceData = stateCopy.step3Data[ip];
      serviceData = serviceData.map((item) => {
        if (item.name == name) {
          let obj = { ...item };
          obj.install_args = obj.install_args.map((i) => {
            if (i.key == key) {
              return {
                ...i,
                default: value,
              };
            }
            return i;
          });
          obj.ports = obj.ports.map((i) => {
            if (i.key == key) {
              return {
                ...i,
                default: value,
              };
            }
            return i;
          });
          return {
            ...obj,
          };
        }
        return item;
      });
      return {
        ...stateCopy,
        step3Data: {
          ...stateCopy.step3Data,
          [ip]: serviceData,
        },
      };

    case actionTypes.CHANGE_STEP3ERRORDATA:
      return {
        ...stateCopy,
        step3ErrorData: action.payload.err,
      };

    default:
      return state;
  }
}

export default reducer;
