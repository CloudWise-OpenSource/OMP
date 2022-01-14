import { OmpContentWrapper, OmpContentNav } from "@/components";
import { useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import Installation from "./tabs/installation"
import Upgrade from "./tabs/upgrade"

const InstallationRecord = () => {
  const history = useHistory();

  const tabKey = useLocation().state?.tabKey
  
  const [currentList, setCurrentList] = useState(tabKey || "installation");

  const contentNavData = [
    {
      name: "installation",
      text: "安装记录",
      handler: () => {
        if (currentList !== "installation") {
          setCurrentList("installation");
        }
      },
    },
    {
      name: "upgrade",
      text: "升级记录",
      handler: () => {
        if (currentList !== "upgrade") {
          setCurrentList("upgrade");
        }
      },
    },
    {
      name: "backoff",
      text: "回滚记录",
      handler: () => {
        if (currentList !== "backoff") {
          setCurrentList("backoff");
        }
      },
    },
  ];

  return (
    <OmpContentWrapper>
      <OmpContentNav data={contentNavData} currentFocus={currentList} />
      {currentList == "installation" && <Installation history={history} /> }
      {currentList == "upgrade" && <Upgrade history={history} /> }
      {currentList == "backoff" && <Upgrade history={history} />}
    </OmpContentWrapper>
  );
};

export default InstallationRecord;
