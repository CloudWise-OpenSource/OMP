import * as actionTypes from "./constants";

export const getSetViewSizeAction = (viewSize) => ({
    type: actionTypes.SET_VIEWSIZE,
    payload: {
        viewSize:viewSize
    }
});