import RenderArr from "./RenderArr";
import RenderNum from "./RenderNum";

const DeployNumRow = ({ data, form }) => {

  return (
    <>
      <div style={{ flex:  1 }}>{data.name}</div>
      <div style={{ flex: 1 }}>{data.version}</div>
      {Array.isArray(data.deploy_mode) ? (
        <RenderArr data={data} form={form} />
      ) : (
        <RenderNum data={data} form={form} />
      )}
      <div
        style={{ flex: 2, display: "flex", justifyContent: "space-between" }}
      ></div>
    </>
  );
};

export default DeployNumRow;
