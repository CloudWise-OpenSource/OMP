import { combineReducers } from "redux";

import { reducer as customBreadcrumbReducer } from "@/components/CustomBreadcrumb/store";
import { reducer as layoutsReducer } from "@/layouts/store";
//import { reducer as warningRecordReducer } from "@/pages/OperationManagement/WarningRecord/store";
import { reducer as systemManagementReducer } from "@/pages/SystemManagement/store";
import { reducer as appStoreReducer } from "@/pages/AppStore/store";
import { reducer as installReducer } from "@/pages/AppStore/config/Installation/store";

const cReducer = combineReducers({
  customBreadcrumb: customBreadcrumbReducer,
  layouts: layoutsReducer,
  // warningRecord:warningRecordReducer,
  systemManagement: systemManagementReducer,
  appStore: appStoreReducer,
  installation: installReducer,
});

export default cReducer;
