const {
  addWebpackAlias,
  override,
  overrideDevServer,
  addLessLoader,
  addPostcssPlugins,
  fixBabelImports,
  addWebpackPlugin,
} = require("customize-cra");
const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");

const path = require("path");
// 跨域配置
const devServerConfig = () => (config) => {
  return {
    ...config,
    proxy: {
      "/api": {
        target: "http://10.0.14.230:19001/", //"http://10.0.7.146:19001/" , //"http://10.0.9.168:19001/" //服务器地址 Xd8r$3jz //http://10.0.22.86:8000/
        changeOrigin: true,
      },
    },
  };
};

module.exports = {
  webpack: override(
    fixBabelImports("import", {
      libraryName: "antd",
      libraryDirectory: "es",
      style: true, //自动打包相关的样式 默认为 style:'css'
    }),
    // 使用less-loader对源码重的less的变量进行重新制定，设置antd自定义主题
    addLessLoader({
      javascriptEnabled: true,
      modifyVars: { "@primary-color": "#4986f7" },
    }),
    // addPostcssPlugins([require("postcss-px2rem-exclude")({
    //     remUnit: 16,
    //     propList: ['*'],
    //     exclude: ''
    // })]),
    addWebpackPlugin(new ProgressBarPlugin()),
    process.env.NODE_ENV === "production" &&
      addWebpackPlugin(
        new UglifyJsPlugin({
          // 开启打包缓存
          cache: true,
          // 开启多线程打包
          parallel: true,
          uglifyOptions: {
            // 删除警告
            warnings: false,
            // 压缩
            compress: {
              // 移除console
              drop_console: true,
              // 移除debugger
              drop_debugger: true,
            },
          },
        })
      ),
    addWebpackAlias({
      "@": path.resolve(__dirname, "./src"),
      assets: path.resolve(__dirname, "./src/assets"),
      components: path.resolve(__dirname, "./src/components"),
      pages: path.resolve(__dirname, "./src/pages"),
      common: path.resolve(__dirname, "./src/common"),
    }),
    (config) => {
      if (process.env.NODE_ENV === "production") config.devtool = false;
      if (process.env.NODE_ENV === "production") {
        const paths = require("react-scripts/config/paths");
        paths.appBuild = path.join(path.dirname(paths.appBuild), "dist");
        config.output.path = path.join(
          path.dirname(config.output.path),
          "dist"
        );
      }
      return config;
    }
  ),
  devServer: overrideDevServer(devServerConfig()),
};
