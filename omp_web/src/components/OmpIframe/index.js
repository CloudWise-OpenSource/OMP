import { useEffect } from "react";
const OmpIframe = ({ showIframe, setShowIframe, iframeSrc }) => {
  useEffect(() => {
    let h = document.getElementById("root").clientHeight;
    document.getElementById("omp_iframe").style.height = h + "px";
    document.getElementById("omp_iframe_container").style.height =
      h + "px";
  }, []);
  let href = window.location.href.split("#")[0];
  return (
    <>
      <div
        id="omp_iframe_container"
        style={{ overflow: "hidden", position: "relative", backgroundColor:"#f6f7f9" }}
      >
        <iframe
          id="omp_iframe"
          style={{
            width:`calc(100% + 70px)`,
            position: "absolute",
          }}
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
