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
