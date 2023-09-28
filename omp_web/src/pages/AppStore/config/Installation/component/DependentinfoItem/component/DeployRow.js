import DeployNumRow from "./DeployNumRow";
import DeployInstanceRow from "./DeployInstanceRow";

const DeployRow = ({ data, form }) => {
  return <>{data.is_use_exist ? <DeployInstanceRow data={data} form={form} /> : <DeployNumRow data={data} form={form} />}</>;
};

export default DeployRow;
