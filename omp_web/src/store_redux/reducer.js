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