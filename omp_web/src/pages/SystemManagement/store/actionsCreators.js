import * as actionTypes from "./constants";

export const getMaintenanceChangeAction = (value) => ({
    type: actionTypes.CHANGE_MAINTENANCE,
    payload: {
        isMaintenance:value
    }
});