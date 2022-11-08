import { Modal, Button } from "antd";
/**
 * @name:
 * @test: test font
 * @msg:
 * @param {*} visibleHandle
 * @param {*} children
 * @return {*}
 */
const OmpMessageModal = ({
  visibleHandle,
  children,
  title,
  onFinish,
  noFooter,
  loading = false,
  afterClose = () => {},
  disabled = false,
  ...residualParam
}) => {
  return (
    <Modal
      {...residualParam}
      title={title}
      visible={visibleHandle[0]}
      //onOk={() => }
      onCancel={() => visibleHandle[1](false)}
      footer={null}
      destroyOnClose
      loading={loading}
      afterClose={afterClose}
    >
      {children}
      <div
        style={{
          textAlign: "center",
          position: "relative",
          top: 0,
          paddingTop: 20,
        }}
      >
        {noFooter ? (
          ""
        ) : (
          <>
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
              disabled={disabled}
            >
              确定
            </Button>
          </>
        )}
      </div>
    </Modal>
  );
};

export default OmpMessageModal;
