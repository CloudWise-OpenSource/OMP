import { useEffect, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { handleResponse } from "@/utils/utils";
import { fetchGet } from "@/utils/request";
import { apiRequest } from "@/config/requestApi";

const ComponentInstallation = () => {
  const history = useHistory();
  let pathArr = history.location.pathname.split("/");
  let name = pathArr[pathArr.length - 1];
  console.log(history, location, name);

  const [loading, setLoading] = useState(false);

  function fetchData() {
    setLoading(true);
    fetchGet(apiRequest.appStore.componentEntrance, {
      params: {
        app_name: name,
      },
    })
      .then((res) => {
        handleResponse(res, (res) => {
          console.log(res);
        });
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetchData()
  }, []);

  return (
    <div>
      <div>jdk</div>
    </div>
  );
};

export default ComponentInstallation;
