import React, { useEffect, useState } from "react";

const Container = ({ children, ...arg }) => {

  let extendChild = React.cloneElement(children, arg);

  return (
    <div
      style={{
        padding: 20,
        paddingTop: 0,
        margin: 10,
        height: "100%",
        overflowY: "auto",
        backgroundColor: "#fff",
      }}
    >
      {extendChild}
    </div>
  );
};
export default Container;
