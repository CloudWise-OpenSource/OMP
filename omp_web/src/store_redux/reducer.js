/*
 * @Author: your name
 * @Date: 2021-06-13 15:26:16
 * @LastEditTime: 2021-06-24 17:18:02
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp_fontend/src/stores/reducer.js
 */

import { combineReducers } from "redux";

import { reducer as customBreadcrumbReducer} from "@/components/CustomBreadcrumb/store";
import { reducer as layoutsReducer } from "@/layouts/store";
import { reducer as warningRecordReducer } from "@/pages/OperationManagement/WarningRecord/store";

const cReducer = combineReducers({
    customBreadcrumb:customBreadcrumbReducer,
    layouts:layoutsReducer,
    warningRecord:warningRecordReducer
});

export default cReducer;