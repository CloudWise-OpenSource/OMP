import { Button } from "antd";

const OmpButton = (props) => {
  return (
    <Button
      ref={
        ((node) => {
          if (node) {
            if(props.disabled){
                node.style.setProperty("color", "#d7d7d7", "important")
                node.style.setProperty("background-color", "#f3f3f3", "important")
            }else{
                node.style.setProperty("color", null)
                node.style.setProperty("background-color", null)
            }
          }
        })
      }
      {...props}
    />
  );
};

export default OmpButton;
