# 自定义脚本模板文件
# 1. 脚本名称须使用蛇形命名法，且以custom_开头
# 2. 类名须为 CustomMetrics
# 3. 函数需以get开头，使用蛇形命名法，须为静态方法，无形参，形如 get_xxx()
# 4. 函数返回数据格式须为json格式，必须包含 help，type，metric，value 键值对，labels键值对可选
# 5. 不可以引用第三方模块
# 以下为参考内容
class CustomMetrics:

    @staticmethod
    def get_node_cpu_guest_seconds_total():
        """
        获取guest占用cpu时间
        :return:
        """
        return {
            "help": "node_cpu_guest_seconds_total Seconds the cpus spent in guests (VMs) for each mode.",
            "type": "counter",
            "metric": "node_cpu_guest_seconds_total",
            "value": 4,
            "labels": {
                "cpu": "0",
                "mode": "nice"
            }
        }

    @staticmethod
    def get_node_runtime():
        """
        获取系统运行时间
        :return:
        """
        return {
            "help": "node runtime.",
            "type": "gauge",
            "metric": "node_runtime",
            "value": 2000,
            "labels": []
        }
