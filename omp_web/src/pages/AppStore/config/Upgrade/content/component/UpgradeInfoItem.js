import UpgradeDetail from "./UpgradeDetail";

const UpgradeInfoItem = ({ id, data, title, log, idx }) => {
  return (
    <div
      id={id}
      style={{
        //marginTop: 20,
        backgroundColor: "#fff",
        padding: 10,
        //marginBottom: 15,
        marginTop: idx !== 0 && 15,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          width: "100%",
          position: "relative",
          height: 40,
          paddingTop: 10,
        }}
      >
        <div
          style={{
            fontWeight: 500,
            position: "absolute",
            left: 30,
            backgroundColor: "#fff",
            paddingLeft: 20,
            paddingRight: 20,
          }}
        >
          {title}
        </div>
        <div style={{ height: 1, backgroundColor: "#b3b2b3", width: "100%" }} />
      </div>
      <div
        style={{
          paddingLeft: 20,
          marginTop: 10,
          paddingBottom: 5,
          // paddingTop: 20,
        }}
      >
        {data?.map((item) => {
          console.log(item);
          return (
            <UpgradeDetail
              title={title}
              key={`${title}=${item.ip}=${item.instance_name}`}
              status={item.upgrade_state}
              ip={item.ip}
              log={item.message}
              instance_name={item.instance_name}
            />
          );
        })}
      </div>
    </div>
  );
};

export default UpgradeInfoItem;
