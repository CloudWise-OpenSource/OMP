import React, { useEffect } from "react";
const OmpIframe = ({ showIframe, setShowIframe, iframeSrc }) => {
  useEffect(() => {
    let h = document.getElementById("root").clientHeight;
    document.getElementById("omp_iframe").style.height = h + 125 + "px";
    document.getElementById("omp_iframe_container").style.height =
      h + "px";
  }, []);
  let href = window.location.href.split("#")[0];
  return (
    <>
      <div
        id="omp_iframe_container"
        style={{ overflow: "hidden", position: "relative",backgroundColor:"#f6f7f9" }}
      >
        <iframe
          id="omp_iframe"
          style={{
            width:`calc(100% + 70px)`,
            position: "absolute",
            //top: showIframe?.isLog?-55:-106,
            //left: -66,
          }}
          //ref="iframe"
          //src={`http://10.0.7.146:19014/proxy/v1/grafana/d/9CWBz0bik/zhu-ji-xin-xi-mian-ban?orgId=1&from=now-5m&to=now`}
          src={showIframe.src}
          width="100%"
          // scrolling="no"
          name="omp_iframe"
          frameBorder="0"
        ></iframe>
      </div>
    </>
  );
};

export default OmpIframe;
