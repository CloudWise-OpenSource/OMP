import * as actionTypes from "./constants";

export const getTabKeyChangeAction = (value) => ({
  type: actionTypes.CHANGE_APPSTORETABKEY,
  payload: {
    appStoreTabKey: value,
  },
});

export const getUniqueKeyChangeAction = (value) => ({
  type: actionTypes.SETUNIQUE_KEY,
  payload: {
    uniqueKey: value,
  },
});
