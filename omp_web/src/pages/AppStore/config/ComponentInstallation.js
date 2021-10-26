import { useEffect } from "react";
import { useHistory, useLocation } from "react-router-dom";

const ComponentInstallation = () => {
  const history = useHistory();
  let pathArr = history.location.pathname.split("/");
  let name = pathArr[pathArr.length - 1];
  console.log(history, location,name);

useEffect(()=>{

},[])

  return <div>
      <div>jdk</div>
  </div>;
};

export default ComponentInstallation;
