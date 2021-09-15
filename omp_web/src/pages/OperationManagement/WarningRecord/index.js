/*
 * @Author: your name
 * @Date: 2021-06-25 15:24:13
 * @LastEditTime: 2021-06-28 17:33:47
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /omp-fontend123/src/pages/ProductsManagement/WarningList/index.js
 */
import { OmpContentNav, OmpContentWrapper } from "@/components";
import { Badge } from "antd";
import { useState } from "react";
import { _idxInit } from "@/utils/utils";
import ServiceTab from "./component/serviceTab";
import HostTab from "./component/hostTab";
import { useSelector } from "react-redux";

const WarningRecord = () => {
  //服务数据
  const [currentList, setCurrentList] = useState("host");

  const { serviceTotal, hostTotal } = useSelector(
    (state) => state.warningRecord
  );

  const contentNavData = [
    {
      name: "host",
      text:
        currentList == "host" ? (
          "主机异常"
        ) : (
          <Badge
            overflowCount={999}
            count={hostTotal}
            size="small"
            offset={[8, -5]}
          >
            主机异常
          </Badge>
        ),
      handler: () => {
        if (currentList !== "host") {
          setCurrentList("host");
        }
      },
    },
    {
      name: "service",
      text:
        currentList == "service" ? (
          "服务异常"
        ) : (
          <Badge
            overflowCount={999}
            count={serviceTotal}
            size="small"
            offset={[8, -5]}
          >
            服务异常
          </Badge>
        ),
      handler: () => {
        if (currentList !== "service") {
          setCurrentList("service");
        }
      },
    },
  ];

  const contentMap = {
    host: <HostTab />,
    service: <ServiceTab />,
  };

  return (
    <OmpContentWrapper>
      <OmpContentNav data={contentNavData} currentFocus={currentList} />
      {contentMap[currentList]}
    </OmpContentWrapper>
  );
};

export default WarningRecord;
