import { Tooltip } from "antd";

const OmpToolTip = ({ children, maxLength, ...props }) => {
  children = children || "-";
  if (children.length > maxLength) {
    return (
      <Tooltip title={children} {...props}>
        {children.substring(0, maxLength)}...
      </Tooltip>
    );
  } else {
    return children;
  }
};

export default OmpToolTip;
