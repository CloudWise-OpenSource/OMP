import { DatePicker } from "antd";
import moment from "moment";

const OmpDatePicker = ({...props}) => {
  return (
    <DatePicker.RangePicker
      ranges={{
        今天: [moment().startOf("day"), moment()],
        本周: [moment().startOf("week"), moment()],
        本月: [moment().startOf("month"), moment()],
      }}
      disabledDate={(current) => {
        return current && current >= moment().endOf("day");
      }}
      showTime={{
        hideDisabledOptions: true,
      }}
      //value={rangePickerValue}
      format="YYYY-MM-DD HH:mm:ss"
      {...props}
      // onChange={onChange}
      // onOk={(dates) => {
      //   const start = moment(dates[0]).format("YYYY-MM-DD HH:mm:ss");
      //   const end = moment(dates[1]).format("YYYY-MM-DD HH:mm:ss");
      //   getServiceData(pagination, {
      //     query_start_time: start,
      //     query_end_time: end,
      //     query_content: searchValue,
      //   });
      // }}
    />
  );
};

export default OmpDatePicker;
