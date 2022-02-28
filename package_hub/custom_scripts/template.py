# Demo
class CustomMetrics:

    @staticmethod
    def get_node_cpu_guest_seconds_total():
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
