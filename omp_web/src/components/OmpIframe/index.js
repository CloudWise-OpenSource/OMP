import React, { useEffect } from "react";
const OmpIframe = ({ isShowIframe, setIsShowIsframe, iframeSrc }) => {
  useEffect(() => {
    let h = document.getElementsByClassName("cw-page-content")[0].clientHeight;
    document.getElementById("omp_iframe").style.height = h + 105 + "px";
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
            top: isShowIframe.isLog?-55:-106,
            left: -66,
          }}
          //ref="iframe"
          src={`${href.substring(0, href.length - 1)}${isShowIframe.src}`}
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
