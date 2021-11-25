import { Tooltip, Spin } from "antd";

const HasInstallService = ({ children, ip, installService }) => {
  
  return (
    <Tooltip
      mouseEnterDelay={0.3}
      placement="right"
      color="#fff"
      title={
        <div
          style={{
            color: "rgba(0, 0, 0, 0.85)",
            padding: 5,
          }}
        >
          <div
            style={{
              borderBottom: "1px solid #d9d9d9",
              fontSize: 13,
              paddingBottom: 5,
            }}
          >
            已选安装服务
          </div>
          <Spin spinning={!installService}>
            <div
              style={{
                overflowY: "auto",
                height: 100,
              }}
            >
            {installService[ip]?.map((item) => {
              return (
                <div
                  style={{ paddingTop: 5, fontSize: 13 }}
                  key={item.service_instance_name}
                >
                  {item.service_instance_name}
                </div>
              );
            })}
            </div>
          </Spin>
        </div>
      }
    >
      <a>{children}</a>
    </Tooltip>
  );
};

export default HasInstallService;
