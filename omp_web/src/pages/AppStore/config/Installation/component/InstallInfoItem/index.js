import InstallDetail from "./component/InstallDetail";
import { useState } from "react";
const InstallInfoItem = ({ id, data, title, openName, setOpenName }) => {
  return (
    <div
      id={id}
      style={{
        //marginTop: 20,
        backgroundColor: "#fff",
        padding: 10,
        marginBottom: 15,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          width: "100%",
          position: "relative",
          height: 30,
        }}
      >
        <div
          style={{
            fontWeight: 500,
            position: "absolute",
            left: 30,
            backgroundColor: "#fff",
            paddingLeft: 20,
            paddingRight: 20,
          }}
        >
          {title}
        </div>
        <div style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }} />
      </div>
      <div
        style={{
          paddingLeft: 20,
          marginTop: 10,
          paddingBottom: 5,
          // paddingTop: 20,
        }}
      >
        {data.map((item) => {
          return (
            <InstallDetail
              title={title}
              openName={openName}
              setOpenName={setOpenName}
              key={`${title}=${item.ip}`}
              status={item.status}
              ip={item.ip}
            />
          );
        })}
      </div>
    </div>
  );
};

export default InstallInfoItem;
