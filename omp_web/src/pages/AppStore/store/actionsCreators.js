import * as actionTypes from "./constants";

export const getTabKeyChangeAction = (value) => ({
    type: actionTypes.CHANGE_APPSTORETABKEY,
    payload: {
        appStoreTabKey:value
    }
});