import { useState, useEffect, useLayoutEffect } from "react";
import styles from "./index.module.less";
import { Form, Input, Button, Select, Drawer, Tag } from "antd";
import { DownOutlined, FunnelPlotFilled, PlusOutlined, CloseOutlined } from "@ant-design/icons";
import { useSelector } from "react-redux";

const OmpCollapseWrapper = ({
  children,
  onFinish,
  form,
  onReset,
  initialValues = {},
  operation,
}) => {
  
  const [defaultForm] = Form.useForm();
  const formInstance = form ? form : defaultForm;
  const [visible, setVisible] = useState(false);

  const [searchTags, setSearchTags] = useState({})

  let childrenArr = Array.isArray(children) ? children : [children];

  // 提取form表单中的数据，将name和label关联起来,如果是select框因为value和text不一致，也要存进来
  // 为了获取检索项的渲染数据
  let dictionary = childrenArr.map(item=>{
    return {
      label: item.props.label,
      name: item.props.name,
      //有children代表是select
      children: item.props.children?.map(i=>i.props)
    }
  })

  const renderButtonGroup = () => {
    return (
      <div style={{ width: "100%", marginLeft: "190px", marginTop: "60px" }}>
        <Form.Item>
          <Button type="primary" htmlType="submit" style={{ marginRight: 10 }}>
            查询
          </Button>
          <Button
            style={{ marginRight: 10 }}
            onClick={() => {
              setSearchTags({})
              formInstance.resetFields();
              onReset && onReset();
              setVisible(false)
            }}
          >
            重置
          </Button>
        </Form.Item>
      </div>
    );
  };

  useEffect(()=>{
    console.log(searchTags)
  },[searchTags])

  return (
    <div
      className={styles.OmpCollapseWrapper}
    >
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <div>{operation}</div>

        <Form
          form={formInstance}
          name="basic"
          className={styles.OmpCollapseFormWrapper}
          layout="inline"
          initialValues={initialValues}
          onFinish={()=>{
            let formData = formInstance.getFieldValue();
            console.log(formData)
            onFinish()
          }}
        >
          <Form.Item
            label="IP地址"
            key="alert_ip"
            name="alert_ip"
            labelAlign="right"
          >
            <Select placeholder="请选择IP地址" style={{ width: 200 }}>
              <Select.Option value="10.0.9.61">10.0.9.61</Select.Option>
              <Select.Option value="10.0.9.62">10.0.9.62</Select.Option>
              <Select.Option value="10.0.9.63">10.0.9.63</Select.Option>
              <Select.Option value="all">全部</Select.Option>
            </Select>
            
          </Form.Item>
          <Button
              onClick={() => {
                setVisible(true);
              }}
              style={{ margin: 10, marginLeft:0,marginRight:15,paddingLeft: 10, paddingRight: 10}}
            >
              <FunnelPlotFilled style={{ position: "relative", top: 1 }} />
            </Button>
         
        </Form>
      </div>
      {Object.keys(searchTags).length>0 && (
        <div style={{position:"relative",top:-5,paddingLeft:5,fontSize:"12px",
        height:25,display:"flex",alignItems:"center"}}>
        <FunnelPlotFilled  /> <span style={{paddingRight:5,paddingLeft:2}}>检索项 : </span>
            {Object.keys(searchTags).map(key=>{
              return (<Tag
              color="#eeeff3"
              style={{height:20,color:"#63656E"}}
              key={key}
              closable
              closeIcon={<CloseOutlined style={{color:"#63656E"}}/>}
              onClose={e => {
                e.preventDefault();
                let willDeleteItem = dictionary.filter(item=>item.label == key)
                formInstance.resetFields([willDeleteItem[0].name])
                setSearchTags((tags)=>{
                  let newTags = {...tags}
                  delete newTags[key]
                  return newTags
                })
              }}
            >
              {`${key}=${searchTags[key]}`}
            </Tag>)
            })}
      </div>
      )}
      <Drawer
        title="高级筛选"
        placement="right"
        onClose={() => setVisible(false)}
        visible={visible}
        width={560}
        bodyStyle={{
          paddingLeft: 20,
          paddingRight: 20,
        }}
      >
        <Form
          form={formInstance}
          name="basic"
          className={styles.OmpCollapseFormWrapper}
          layout="inline"
          initialValues={initialValues}
          //onFinish={onFinish}
          onFinish={(e)=>{
            let formData = formInstance.getFieldValue();
            //console.log(formData,e,childrenArr)
            Object.keys(formData).map(i=>{
              let [info] = dictionary.filter(item=>item.name == i)
              // console.log(info,formData[i])
              if(formData[i]){
                let value = formData[i]
                //如果是select，要展示text，根据value检索text
                if(info.children){
                  info.children.map(c=>{
                    if(c.value == value){
                      value = c.children
                    }
                  })
                }
                setSearchTags(tags=>{
                  return {
                    ...tags,
                    [info.label] : value
                  }
                })
              }
            })
            setVisible(false)
            onFinish()
          }}
        >
          {childrenArr.map((item) => {
            return (
              <div key={item.props.label}>
                <Form.Item
                  label={<span style={{ width: 65 }}>{item.props.label}</span>}
                  key={item.props.label}
                  name={item.props.label && item.props.name}
                  labelAlign="right"
                  style={{ width: `242px`, marginBottom: 15 }}
                >
                  {item}
                </Form.Item>
              </div>
            );
          })}
          {renderButtonGroup()}
        </Form>
      </Drawer>
    </div>
  );
};

export default OmpCollapseWrapper;
