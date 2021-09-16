import { useState, useEffect, useLayoutEffect } from "react";
import styles from "./index.module.less";
import { Form, Input, Button } from "antd";
import {
  DownOutlined,
} from "@ant-design/icons";
import { useSelector } from "react-redux";

const OmpCollapseWrapper = ({ children, onFinish, form, onReset, initialValues={} }) => {
  const [isExpand, setIsExpand] = useState(false)
  const [ defaultForm ] = Form.useForm();
  const formInstance = form?form:defaultForm
  let childrenArr = Array.isArray(children) ? children : [children];
  // 视口宽度
  const viewWidth = useSelector(state => state.layouts.viewSize.width);
  //每个formitem 的初始值定为255
  const [itemWidth, setItemWidth] = useState(255)
  // 计算当前组件的宽度 = 窗口宽度 - 左侧asideMenu宽度 - content区域的padding*2
  let width = viewWidth - 240 - 20*2
  // 计算在当前窗口宽度下，一行能放置几个formItem
  let num = (width - 240)/itemWidth
  let widthSurplus = (width - 240)%itemWidth/num

  //console.log(width,num,widthSurplus)

  useLayoutEffect(()=>{
    // 根据剩余宽度重新计算每个foritem的宽度（目的是当剩余宽度过多，增加formitem宽度）
    setItemWidth((w)=>w + Number(widthSurplus) - 28)
  },[])

  let result = childrenArr.slice(0,num)

  const renderButtonGroup = ()=>{
    return (
      <div style={{ position:"absolute", right:0,bottom:0 }}>
          <Form.Item style={{ float: "right",marginLeft:"auto" }}>
            <div style={{ float: "right" }}>
              <Button
                type="primary"
                htmlType="submit"
                style={{ marginRight: 10 }}
              >
                查询
              </Button>
              <Button style={{ marginRight: 10 }} onClick={()=>{formInstance.resetFields();onReset&&onReset()}}>重置</Button>
              {
                childrenArr.length > num &&  <span style={{ color: "#1890ff", fontSize: 14, position:"relative", top:2, cursor:"pointer" }} onClick={()=>setIsExpand(!isExpand)}>
                <DownOutlined style={{position:"relative",top:"1px"}} rotate={isExpand?180:0}/>
                 {isExpand?" 收起":" 展开"}
              </span>
              }
            </div>
          </Form.Item>
        </div>
    )
  }

  return (
    <div 
    //ref={measuredRef} 
    //id="warpper" 
    //onClick={()=> console.log(height)} 
    className={styles.OmpCollapseWrapper} 
  //  / style={{height:60,overflow:"hidden"}}
    >
      <Form
        form = {formInstance}
        name="basic"
        className={styles.OmpCollapseFormWrapper}
        layout="inline"
        initialValues={initialValues}
        onFinish={onFinish}
      >
        {(isExpand?childrenArr:result).map((item) => {
          return (
            <div key={item.props.label}>
              <Form.Item
                label={<span style={{ width: 70 }}>{item.props.label}</span>}
                key={item.props.label}
                name={item.props.label && item.props.name}
                labelAlign="right"
                style={{width:item.props.width || `${itemWidth}px`}}
              >
                {item}
              </Form.Item>
            </div>
          );
        })}
        <div style={{height:45,width:itemWidth}}><div></div></div>
        {renderButtonGroup()}
      </Form>
    </div>
  );
};

export default OmpCollapseWrapper;
