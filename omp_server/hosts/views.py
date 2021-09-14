"""
主机相关视图
"""

from rest_framework.views import APIView
from rest_framework.response import Response

from db_models.models import UserProfile
from hosts.tasks import test_task


class HostsTestView(APIView):
    queryset = UserProfile.objects.all()

    def post(self, request):
        # print(request)
        # from datetime import datetime
        # from datetime import timedelta
        # from django_celery_beat.schedulers import ClockedSchedule
        # from django_celery_beat.schedulers import CrontabSchedule
        # from django_celery_beat.schedulers import PeriodicTask
        # def test_clock():
        #     clock = ClockedSchedule.objects.create(clocked_time=datetime.now() + timedelta(seconds=10))
        #     PeriodicTask.objects.create(
        #         name="%s" % str(datetime.now()),
        #         task="hosts.tasks.test_task",
        #         clocked=clock,
        #         # 如果使用ClockedSchedule，则one_off必须为True
        #         one_off=True
        #     )
        # # test_task.delay(1, 2)
        # # test_clock()
        # import json
        # def test_crontab():
        #     # 表示 * * * * * ，即每隔一分钟触发一次
        #     schedule = CrontabSchedule.objects.create(timezone='Asia/Shanghai')
        #     PeriodicTask.objects.create(
        #         name="%s" % str(datetime.now()),
        #         task="hosts.tasks.test_task",
        #         crontab=schedule,
        #         one_off=True,
        #         args=json.dumps([1, 2])
        #     )
        # test_crontab()
        return Response("success")
