import * as actionTypes from "./constants";

const defaultState = {
  appStoreTabKey: "component",
  uniqueKey: "",
};

function reducer(state = defaultState, action) {
  switch (action.type) {
    case actionTypes.CHANGE_APPSTORETABKEY:
      return { ...state, appStoreTabKey: action.payload.appStoreTabKey };
    case actionTypes.SETUNIQUE_KEY:
      return { ...state, uniqueKey: action.payload.uniqueKey };
    default:
      return state;
  }
}

export default reducer;
