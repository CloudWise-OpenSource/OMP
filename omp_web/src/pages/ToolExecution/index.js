import { useState } from "react";
import { Button, Form, Spin, Input, InputNumber } from "antd";
import { useHistory, useLocation } from "react-router-dom";
import {
  OmpContentWrapper,
  OmpTable,
  OmpMessageModal,
  OmpSelect,
  OmpDatePicker,
  OmpDrawer,
} from "@/components";
import styles from "./index.module.less";

const ToolExecution = () => {
  const history = useHistory();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  return (
    <OmpContentWrapper
      wrapperStyle={{ padding: 0, paddingBottom: 30, backgroundColor: "#fff" }}
    >
      <div className={styles.header}>
        <div>创建任务: kafaka生产者&消费者</div>
        <Button>返回</Button>
      </div>
      <div style={{ paddingTop: 20 }}>
        <Spin spinning={loading}>
          <Form
            name="implement"
            labelCol={{ span: 3 }}
            wrapperCol={{ span: 6 }}
            style={{ paddingTop: 10 }}
            onFinish={() => {}}
            form={form}
          >
            <Form.Item
              label="任务标题"
              name="title"
              rules={[{ required: true, message: "请输入任务标题" }]}
            >
              <Input
                placeholder="请输入任务标题"
                style={{
                  width: 460,
                }}
              />
            </Form.Item>
            <Form.Item
              label="执行对象"
              name="object"
              rules={[{ required: true, message: "请输入执行对象" }]}
            >
              <Input
                placeholder="请输入执行对象"
                style={{
                  width: 460,
                }}
              />
            </Form.Item>
            <Form.Item
              label="超时时间"
              name="time"
              rules={[{ required: true, message: "请输入执行对象" }]}
            >
              <InputNumber min={1} max={10} defaultValue={3} /> 秒
            </Form.Item>
            <Form.Item
              label="执行用户"
              name="user"
              rules={[{ required: true, message: "请输入执行用户" }]}
            >
              <Input
                placeholder="请输入执行用户"
                style={{
                  width: 160,
                }}
              />
            </Form.Item>
          </Form>
        </Spin>
        {/* 工具执行：域名&IP连通性检查
        <Button
          onClick={() => {
            history?.push({
              pathname: `/utilitie/tool-management/tool-execution-results/123`,
            });
          }}
        >
          查看执行结果
        </Button> */}
      </div>
    </OmpContentWrapper>
  );
};

export default ToolExecution;
