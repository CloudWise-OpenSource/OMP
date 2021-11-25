import styles from "../index.module.less";
import JdkRow from "./component/JdkRow";
import DeployRow from "./component/DeployRow";

const DependentInfoItem = ({ data, form }) => {
  //   useEffect(() => {
  //     form.setFieldsValue({
  //       [`${data.name}`]: `${data.name}-${randomNumber()}`,
  //     });
  //     data.services_list.map((item) => {
  //       form.setFieldsValue({
  //         [`${data.name}=${item.name}`]: `${item.deploy_mode.default}`,
  //       });
  //     });
  //   }, []);

  return (
    <>
      <div className={styles.dependentinfoItem}>
        {data.is_base_env ? (
          <JdkRow data={data} />
        ) : (
          <DeployRow data={data} form={form} />
        )}
      </div>
      <div
        style={{
          marginTop: 5,
          color: "red",
          height: data.error_msg ? 20 : 0,
          transition: "all .2s ease-in",
        }}
      >
        {data.error_msg}
      </div>
    </>
  );
};

export default DependentInfoItem;
