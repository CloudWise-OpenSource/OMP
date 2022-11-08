import logging
import threading
import traceback

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend

from db_models.models import EmailSMTPSetting

logger = logging.getLogger("server")


class ResultThread(threading.Thread):
    """
    需要运行结果的多线程
    """

    def __init__(self, target, args, name=''):
        threading.Thread.__init__(self)
        self.target = target
        self.name = name
        self.args = args

    def run(self):
        self.result = self.target(*self.args)

    def get_result(self):
        return self.result


class ModelSettingEmailBackend:
    # 邮件 SMTP 服务器链接backend(修改默认的settings)

    @property
    def load_settings(self):
        if hasattr(self, "setting_kwargs"):
            return self.setting_kwargs
        setting_obj = EmailSMTPSetting.objects.first()
        setting_kwargs = {}
        if setting_obj:
            setting_kwargs = setting_obj.get_dict()
        setattr(self, "setting_kwargs", setting_obj.get_dict())
        return setting_kwargs

    def load_connection(self):
        setting_kwargs = self.load_settings
        if not setting_kwargs:
            return None
        return EmailBackend(**setting_kwargs)


class SendEmailContent:
    # 邮件内容基类
    subject = ""  # 邮件主题
    from_user = "运维管理平台<{}>"  # 发件人
    is_html = False  # 是否是html邮件
    file = False  # 存在的文件使用
    file_content = False  # 临时文件使用

    def __init__(self, _obj):
        self._obj = _obj

    @property
    def fetch_content(self):
        # 获取邮件内容
        if hasattr(self, "email_content"):
            return self.email_content
        email_content = self._obj.send_email_content()
        setattr(self, "email_content", email_content)
        return email_content

    def fetch_html_content(self):
        # 获取邮件html内容
        pass

    def fetch_file_kwargs(self):
        # 文件
        if hasattr(self, "file_kwargs"):
            return self.file_kwargs
        file_kwargs = self._obj.fetch_file_kwargs()
        setattr(self, "file_kwargs", file_kwargs)
        return file_kwargs

    def fetch_file_content(self):
        if hasattr(self, "file_content"):
            return self.file_content
        file_content = self._obj.fetch_file_content()
        setattr(self, "file_content", file_content)
        return file_content


class SendAlertEmailContent(SendEmailContent):
    subject = "运维管理平台警消息通知"


class SendBackupHistoryEmailContent(SendEmailContent):
    subject = "运维管理平台备份通知邮件"
    file = True


class SendDeepInspectionEmailContent(SendBackupHistoryEmailContent):
    subject = "运维管理平台深度巡检报告通知邮件"
    file = True


class SendNormalInspectionEmailContent(SendBackupHistoryEmailContent):
    subject = "运维管理平台主机、组件巡检报告通知邮件"
    file = True


class EmailSendTool(object):
    # 邮件发送

    def __init__(self, con_backend, content, users):
        from_user = content.from_user.format(
            con_backend.load_settings.get("username"))
        self.email_msg = EmailMultiAlternatives(
            content.subject,
            content.fetch_content,
            from_user,
            users,
            connection=con_backend.load_connection()
        )
        self.content = content
        self.need_send_count = len(users)

    def send(self):
        """
        发送邮件
        :return:
        """
        try:
            if self.content.is_html:
                self.email_msg.attach_alternative(
                    self.content.fetch_html_content, "text/html")
            if self.content.file:
                self.email_msg.attach_file(
                    **self.content.fetch_file_kwargs()
                )
            elif self.content.file_content:
                self.email_msg.attach(
                    **self.content.fetch_file_content()
                )
        except Exception as e:
            logger.error(f"发送邮件失败，失败原因： {str(e)}，详情为：{traceback.format_exc()}")
        try:
            count = self.email_msg.send()
        except Exception as e:
            logger.error(f"发送邮件失败，失败原因：{str(e)}")
            return False
        if self.need_send_count - count:
            return False
        return True


def many_send(connection, content, users):
    """
    多个并发同时发送，用以区分失败人
    :param connection: 邮件服务器配置对象：ModelSettingEmailBackend
    :param content:  邮件内容对象：SendEmailContent
    :param users: 用户邮箱list、set
    :return:
    """

    threading_list = []
    for user in users:
        send_tool = EmailSendTool(connection, content, (user,))
        _thread = ResultThread(
            target=send_tool.send,
            args=())
        threading_list.append(_thread)
    threading_list_result = []
    [thread_obj.start() for thread_obj in threading_list]

    for thread_obj in threading_list:
        thread_obj.join()
        threading_list_result.append(thread_obj.get_result())
    fail_user = []
    for user, result in zip(users, threading_list_result):
        if not result:
            fail_user.append(user)
    return fail_user
