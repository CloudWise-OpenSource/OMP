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
