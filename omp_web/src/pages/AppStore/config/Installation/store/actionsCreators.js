import * as actionTypes from "./constants";
import * as R from "ramda"

export const getDataSourceChangeAction = (value) => {
  const dataSource = R.clone(value);
  return {
    type: actionTypes.CHANGE_DATASOURCE,
    payload: {
      dataSource: dataSource,
    },
  };
};

export const getIpListChangeAction = (value) => {
  const list = R.clone(value);
  return {
    type: actionTypes.CHANGE_IPLIST,
    payload: {
      ipList: list,
    },
  };
};

export const getStep1ChangeAction = (value) => {
  const data = R.clone(value);
  return {
    type: actionTypes.CHANGE_STEP1DATA,
    payload: {
      step1Data: data,
    },
  };
};

export const getStep2ChangeAction = (value) => {
  const data = R.clone(value);
  return {
    type: actionTypes.CHANGE_STEP2DATA,
    payload: {
      step2Data: data,
    },
  };
};

export const getStep3ChangeAction = (value) => {
  const data = R.clone(value);
  return {
    type: actionTypes.CHANGE_STEP3DATA,
    payload: {
      step3Data: data,
    },
  };
};