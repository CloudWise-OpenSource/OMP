import { Modal, Button, Form } from "antd";
import React from "react";
import styles from "./index.module.less";

const OmpModal = ({
  visibleHandle,
  children,
  title,
  onFinish = () => {},
  footer,
  loading = false,
  afterClose = () => {},
  form,
  initialValues = {},
  setLoading,
  okBtnText,
  beForeOk = () => {},
  formLabelCol = { span: 7 },
  formWrapperCol = { span: 14 },
  ...residualParam
}) => {
  const [modalForm] = Form.useForm();
  // 扩展formItem功能,为了能够在formitem的validator校验时获得当前form的实例进行操作
  // 在这里重写formitem的validator函数，在新函数中注入form实例
  // console.log(children)
  let dealChild = Array.isArray(children) ? children : [children];
  let processedChildren = dealChild?.map((item) => {
    if (item.props?.useforminstanceinvalidator === "true") {
      // 当前就是需要扩展validator的formItem
      // 拿到当前项的rules数组并把数组项为{validator:fn}的拿到，重写fn
      let newRules = item.props.rules.map((r) => {
        if (r.validator) {
          //重写validator
          return {
            validator: (rule, value, callback) => {
              return r.validator(rule, value, callback, modalForm);
            },
          };
        } else {
          return r;
        }
      });
      return React.cloneElement(item, { rules: newRules });
    } else if (item.props?.useforminstanceinonchange === "true") {
      let newOnChange = (e) => {
        item.props.onChange(e, modalForm);
      };
      return React.cloneElement(item, { onChange: newOnChange });
    } else {
      return item;
    }
  });

  return (
    <Modal
      className={styles.OmpModalWrapper}
      title={title}
      visible={visibleHandle[0]}
      //onOk={() => onOk()}
      onCancel={() => visibleHandle[1](false)}
      footer={footer}
      destroyOnClose
      loading={loading}
      afterClose={() => {
        // 重置表单数据
        form ? form.resetFields() : modalForm.resetFields();
        //传入的afterClose
        afterClose();
      }}
      footer={null}
      {...residualParam}
    >
      <Form
        //style={{ paddingLeft: 50, paddingRight: 50 }}
        form={form ? form : modalForm}
        labelCol={formLabelCol}
        wrapperCol={formWrapperCol}
        onFinish={onFinish}
        initialValues={initialValues}
      >
        {processedChildren}
        <Form.Item
          wrapperCol={{ span: 24 }}
          style={{ textAlign: "center", position: "relative", top: 20 }}
        >
          <Button
            style={{ marginRight: 16 }}
            onClick={() => visibleHandle[1](false)}
          >
            取消
          </Button>
          <span
            onClick={() => {
              beForeOk();
            }}
          >
            <Button loading={loading} type="primary" htmlType="submit">
              {okBtnText || "确定"}
            </Button>
          </span>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default OmpModal;
