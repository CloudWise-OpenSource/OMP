import { Modal, Button } from "antd";
/**
 * @name:
 * @test: test font
 * @msg:
 * @param {*} visibleHandle
 * @param {*} children
 * @return {*}
 */
const OmpMessageModal = ({ visibleHandle, children, title, onFinish, footer, loading=false, afterClose=()=>{}}) => {
  return (
    <Modal
      title={title}
      visible={visibleHandle[0]}
      //onOk={() => }
      onCancel={() => visibleHandle[1](false)}
      footer={null}
      destroyOnClose
      loading={loading}
      afterClose = {afterClose}
    >
      {children}
      <div
          style={{ textAlign: "center", position: "relative", top: 0, paddingTop:20 }}
        >
          <Button
            style={{ marginRight: 16 }}
            onClick={() => visibleHandle[1](false)}
          >
            取消
          </Button>
          <Button
            loading={loading}
            type="primary"
            htmlType="submit"
            onClick={onFinish}
          >
            确定
          </Button>
        </div>
    </Modal>
  );
};

export default OmpMessageModal;