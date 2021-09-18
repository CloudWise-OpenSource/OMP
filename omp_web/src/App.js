import Router from "./router.js";
import { Provider } from "react-redux";
import store from "./store_redux/reduxStore";
// 国际化
import zhCN from 'antd/es/locale/zh_CN';
import { ConfigProvider } from "antd";
import 'moment/locale/zh-cn'

const App = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Provider store={store}>
        <Router />
      </Provider>
    </ConfigProvider>
  );
};

export default App;