/*
 * @Author: your name
 * @Date: 2021-06-13 16:00:50
 * @LastEditTime: 2021-06-21 15:47:47
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp_fontend/src/pages/ProductsManagement/VersionManagement/InstallationDetails/store/actionsCreators.js
 */
import * as actionTypes from "./constants";

export const getMaintenanceChangeAction = (value) => ({
    type: actionTypes.CHANGE_MAINTENANCE,
    payload: {
        isMaintenance:value
    }
});